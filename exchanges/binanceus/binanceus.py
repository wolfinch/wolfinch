#! /usr/bin/env python
# '''
#  OldMonk Auto trading Bot
#  Desc: Binance exchange interactions for OldMonk
#  (c) Joshith
# '''

import json
import pprint
from decimal import Decimal
from datetime import datetime, timedelta
from time import sleep
import time
from dateutil.tz import tzlocal, tzutc
from twisted.internet import reactor

from binance.enums import *
from binance.client import Client
import binance
from binance.websockets import BinanceSocketManager

from utils import getLogger, readConf
from market import Market, OHLC, feed_enQ, get_market_by_product, Order
from exchanges import Exchange

log = getLogger ('BinanceUS')
log.setLevel(log.DEBUG)

# BINANCE CONFIG FILE
BINANCE_CONF = 'config/binanceus.yml'
BNC_INTERVAL_MAPPING = {300 :'5m', 600: '10m'}


class BinanceUS (Exchange):
    name = "binanceus"
    binance_conf = {}
    binance_products = []
    binance_accounts = {}
    public_client = None
    auth_client = None
    ws_client = None
    ws_auth_client = None
    symbol_to_id = {}
    primary = False

    def __init__(self, config, primary=False):
        log.info ("Init Binance exchange")
        
        exch_cfg_file = config['config']
        
        conf = readConf (exch_cfg_file)
        if (conf != None and len(conf)):
            self.binance_conf = conf['exchange']
        else:
            return None
        
        self.primary = True if primary else False
        # get config
        backfill = config.get('backfill')
        if not backfill:
            log.fatal("Invalid backfill config")            
            return None
    
        if backfill.get('enabled'):
            self.binance_conf['backfill_enabled'] = backfill['enabled']
        if backfill.get('period'):
            self.binance_conf['backfill_period'] = int(backfill['period'])
        if backfill.get('interval'):
            # map interval in to binance format
            interval = BNC_INTERVAL_MAPPING[int(backfill['interval']) ]
            self.binance_conf['backfill_interval'] =  interval
            self.candle_interval = int(backfill['interval'])
        
        # for public client, no need of api key
        self.public_client = Client("", "")
        if (self.public_client) == None :
            log.critical("binance public client init failed")
            return None
        
        #get data from exch conf
        self.key = self.binance_conf.get('apiKey')
        self.b64secret = self.binance_conf.get('apiSecret')
        self.test_mode = self.binance_conf.get('test_mode') or False
        
        if ((self.key and self.b64secret) == False):
            log.critical ("Invalid API Credentials in binance Config!! ")
            return None
        
        self.auth_client = Client(self.key, self.b64secret)
        
        if self.auth_client == None:
            log.critical("Unable to Authenticate with binance exchange. Abort!!")
            return None
            
#         global binance_products
        exch_info = self.public_client.get_exchange_info()
        serverTime = long(exch_info['serverTime'])
        localTime = long(time.time() * 1000)
        self.timeOffset = (serverTime - localTime) // 1000
        # if time diff is less the 5s, ignore. 
        if abs(self.timeOffset) < 5: 
            self.timeOffset = 0
        
        log.info ("servertime: %d localtime: %d offset: %d" % (serverTime, localTime, self.timeOffset))
        
#         self.binance_conf['products'] = []
#         for p in config['products']:
#             # add the product ids
#             self.binance_conf['products'] += p.keys()
                    
        products = exch_info.get("symbols")
        log.info ("products: %s" % (pprint.pformat(products, 4)))
                
        if (len(products) and len (self.binance_conf['products'])):
            for prod in products:
                for p in self.binance_conf['products']:
                    for k, v in p.iteritems():
#                         log.debug ("pk: %s s: %s"%(k, prod['symbol']))
                        if prod['symbol'] == k:
                            log.debug ("product found: %s v: %s" % (prod, v))
                            prod['id'] = v['id']
                            prod['display_name'] = k
                            self.symbol_to_id[k] = prod['id']
                            prod ['asset_type'] = prod['baseAsset']
                            prod ['fund_type'] = prod['quoteAsset']
                                                  
                            self.binance_products.append(prod)
        
        # EXH supported in spectator mode. 
        # Popoulate the account details for each interested currencies
        accounts = self.auth_client.get_account()
        if (accounts == None):
            log.critical("Unable to get account details!!")
            return False
        log.debug ("Exchange Accounts: %s" % (pprint.pformat(accounts, 4)))
        balances = accounts ['balances']
        for balance in balances:
#             log.debug ("balance: %s"%(balance))
            for prod in self.binance_products:
                log.debug ("prod_id: %s" % (prod['id']))               
                if balance['asset'] in [prod ['asset_type'], prod ['fund_type']]:
                    log.debug ("Interested Account Found for Currency: " + balance['asset'])
                    self.binance_accounts[balance['asset']] = balance
                    break  
        
        ### Start WebSocket Streams ###
        self.ws_client = bm = BinanceSocketManager(self.public_client)
        symbol_list = []
        for prod in self.get_products():
            # Start Kline socket
#             backfill_interval = self.binance_conf.get('backfill_interval')
#             bm.start_kline_socket(prod['symbol'], self._feed_enQ_msg, interval=backfill_interval)
#             bm.start_aggtrade_socket(prod['symbol'], self._feed_enQ_msg)
            symbol_list.append(prod['symbol'].lower()+"@trade")
            
        if len(symbol_list):
            #start mux ws socket now
            log.info ("starting mux ws sockets for syms: %s"%(symbol_list))
            bm.start_multiplex_socket(symbol_list, self._feed_enQ_msg)
            
        self.ws_auth_client = bm_auth = BinanceSocketManager(self.auth_client)
        # Start user socket for interested symbols
        log.info ("starting user sockets")
        bm_auth.start_user_socket(self._feed_enQ_msg)            

        bm.start()
        bm_auth.start()
        
        log.info("**BinanceUS init success**\n Products: %s\n Accounts: %s" % (
                        pprint.pformat(self.binance_products, 4), pprint.pformat(self.binance_accounts, 4)))
        
    def __str__ (self):
        return "{Message: Binance Exchange }"

    ######## Feed Consume #######
    def _feed_enQ_msg (self, msg_raw):
            log.debug("message :%s " % msg_raw)
            
            if msg_raw.get('stream'):
                msg = msg_raw.get('data')
            else:
                msg = msg_raw

            msg_type = msg.get('e')
            
            if (msg_type == 'aggTrade' or msg_type == 'trade'):
                log.debug ("aggTrade/trade")
                symbol = msg.get("s")            
                product_id = self.symbol_to_id.get(symbol)
                if not product_id:
                    log.error ("unknown market(%s)"%(symbol))
                    return 
                market = get_market_by_product (self.name, product_id)
                if (market == None):
                    log.error ("Feed Thread: Unknown market product: %s: msg %s" % (
                        product_id, json.dumps(msg, indent=4, sort_keys=True)))
                    return
                feed_enQ(market, msg)
            elif (msg_type == 'kline'):
                log.debug ("kline")
                symbol = msg.get("s")            
                product_id = self.symbol_to_id.get(symbol)
                if not product_id:
                    log.error ("unknown market(%s)"%(symbol))
                    return 
                k = msg.get('k')
                if k.get('x') == True:
                    # This kline closed, this is a candle
                    market = get_market_by_product (self.name, product_id)
                    if (market == None):
                        log.error ("Feed Thread: Unknown market product: %s: msg %s" % (
                            product_id, json.dumps(msg, indent=4, sort_keys=True)))
                        return                    
                    feed_enQ(market, msg)
                else:
                    # not interested
                    pass                
            elif (msg_type == 'executionReport'):
                log.debug ("USER DATA: executionReport")
                symbol = msg.get("s")            
                product_id = self.symbol_to_id.get(symbol)
                if not product_id:
                    log.error ("unknown market(%s)"%(symbol))
                    return         
                market = get_market_by_product (self.name, product_id)
                if (market == None):
                    log.error ("Feed Thread: Unknown market product: %s: msg %s" % (
                        product_id, json.dumps(msg, indent=4, sort_keys=True)))
                    return
                feed_enQ(market, msg)
            elif (msg_type == 'error'):
                log.critical("websocket connection retries exceeded!!")
                raise Exception("websocket connection retries exceeded!!")
            else:
                log.error ("Unknown feed. message type: %s prod: %s" % (msg_type, product_id))
            return
                
    def _binance_consume_feed (self, market, msg):
#                         ''' 
#         Feed Call back for Binance    
#         This is where we do all the useful stuff with Feed
#         '''
        msg_type = msg.get('e') 
        if (msg_type == 'trade' or msg_type == 'aggTrade'):
            self._binance_consume_trade_feed (market, msg)            
        elif (msg_type == 'executionReport'):
            log.debug ("Feed: executionReport msg: %s" % (msg))
        elif (msg_type == 'kline'):
            self._binance_consume_candle_feed(market, msg)
                    
    def _binance_consume_trade_feed (self, market, msg):
#         {
#           "e": "aggTrade|trade",  // Event type
#           "E": 123456789,   // Event time
#           "s": "BNBBTC",    // Symbol
#           "a": 12345,       // Aggregate trade ID
#           "p": "0.001",     // Price
#           "q": "100",       // Quantity
#           "f": 100,         // First trade ID
#           "l": 105,         // Last trade ID
#           "T": 123456785,   // Trade time
#           "m": true,        // Is the buyer the market maker?
#           "M": true         // Ignore
#         }        
        log.debug ("Trade feed: %s" % (msg))
        price = Decimal(msg.get('p'))
        last_size = msg.get('q')
        market.tick (price, last_size)
                
    def _binance_consume_candle_feed (self, market, msg):
        log.info ("msg: %s" % msg)
#         msg_type = msg.get('e')
        k = msg.get('k')
        t = long(k.get('T') + 1) // 1000 + self.timeOffset
        o = Decimal(k.get('o'))
        h = Decimal(k.get('h'))
        l = Decimal(k.get('l'))
        c = Decimal(k.get('c'))
        v = Decimal(k.get('v'))
        
#         if now >= market.cur_candle_time + interval:
            # close the current candle period and start a new candle period
        candle = OHLC(long(t), o, h, l, c, v)
        log.debug ("New candle identified %s" % (candle))        
        market.O = market.V = market.H = market.L = 0
        market.add_new_candle (candle)
        
        # TODO: FIXME: jork: might need to rate-limit the logic here after
        market.set_market_rate (c)
#         market.update_market_states()        
            
    #### Feed consume done #####    
    def market_init (self, market):
#         global ws_client
        usd_acc = self.binance_accounts[market.get_fund_type()]
        crypto_acc = self.binance_accounts.get(market.get_asset_type())
        if (usd_acc == None or crypto_acc == None): 
            log.error ("No account available for product: %s"%(market.product_id))
            return None
        
#         #Setup the initial params
        market.fund.set_initial_value(Decimal(usd_acc['free']))
        market.fund.set_hold_value(Decimal(usd_acc['locked']))
        market.asset.set_initial_size(Decimal( crypto_acc['free']))
        market.asset.set_hold_size( Decimal(crypto_acc['locked']))
        
        ## Feed Cb
        market.register_feed_processor(self._binance_consume_feed)
        
        ## Init Exchange specific private state variables
        market.set_candle_interval (self.candle_interval)
        
#         #set whether primary or secondary
#         market.primary = self.primary
        log.info ("Market init complete: %s" % (market.product_id))
                
        return market

    def close (self):
        log.debug("Closing exchange...")    
#         global self.ws_client
        if (self.ws_client):
            log.debug("Closing WebSocket Client")
            self.ws_client.close ()
            self.ws_client.join(1)
        if (self.ws_auth_client):
            log.debug("Closing WebSocket Auth Client")
            self.ws_auth_client.close ()
            self.ws_auth_client.join(1)
        
        if (self.ws_auth_client or self.ws_client):
            if not reactor._stopped:
                reactor.stop()
        log.debug("Closed websockets")

    def get_products (self):
        log.debug ("products num %d" % (len(self.binance_products)))
        return self.binance_products    

    def get_accounts (self):
    #     log.debug (pprint.pformat(self.binance_accounts))
        log.debug ("get accounts")
        return self.binance_accounts    

    def get_historic_rates (self, product_id, start=None, end=None):
        '''
            Args:
        product_id (str): Product
        start (Optional[str]): Start time in ISO 8601
        end (Optional[str]): End time in ISO 8601
        interval (Optional[str]): Desired time slice in 
         seconds
         '''
        # Max Candles in one call
        epoch = datetime.utcfromtimestamp(0).replace(tzinfo=tzutc())
        max_candles = 200
        candles_list = []
        
        # get config
        enabled = self.binance_conf.get('backfill_enabled')
        period = int(self.binance_conf.get('backfill_period'))
        interval_str = self.binance_conf.get('backfill_interval')
        
        interval = binance.helpers.interval_to_milliseconds(interval_str)
        if (interval == None):
            log.error ("Invalid Interval - %s" % interval_str)
        
        product = None
        for p in self.get_products():
            if p['id'] == product_id:
                product = p
        
        if product is None:
            log.error ("Invalid Product Id: %s" % product_id)
            return None
        
        if not enabled:
            log.debug ("Historical data retrieval not enabled")
            return None
    
        if not end:
            # if no end, use current time
            end = datetime.now()
            end = end.replace(tzinfo=tzlocal())
             
        if not start:
            # if no start given, use the config
            real_start = start = end - timedelta(days=period) - timedelta(seconds=interval // 1000)
        else:
            real_start = start
            
        real_start = start = start.replace(tzinfo=tzlocal())
        
        log.debug ("Retrieving Historic candles for period: %s to %s" % (
                    real_start.isoformat(), end.isoformat()))
        
        td = max_candles * interval // 1000
        tmp_end = start + timedelta(seconds=td)
        tmp_end = min(tmp_end, end)
        
        # adjust time with server time
        start = start + timedelta(seconds=self.timeOffset)
        tmp_end = tmp_end + timedelta(seconds=self.timeOffset)
        
        count = 0
        while (start < end):
            # # looks like there is a rate=limiting in force, we will have to slow down
            count += 1
            if (count > 3):
                # rate-limiting
                count = 0
                sleep (2)
            
            start_ts = int((start - epoch).total_seconds() * 1000.0)
            end_ts = int((tmp_end - epoch).total_seconds() * 1000.0)
            
            log.debug ("Start: %s end: %s" % (start_ts, end_ts))
            candles = self.public_client.get_klines (
                symbol=product['symbol'],
                interval=Client.KLINE_INTERVAL_5MINUTE,
                limit=max_candles,
                startTime=start_ts,
                endTime=end_ts
            )
            if candles:
                if isinstance(candles, dict):
                    # # Error Case
                    err_msg = candles.get('message')
                    if (err_msg):
                        log.error ("Error while retrieving Historic rates: msg: %s\n will retry.." % (err_msg))
                else:
                    # candles are of struct [[time, o, h, l,c, V]]
                    candles_list += map(
                        lambda candle: OHLC(time=long(candle[6] + 1) // 1000,
                                            low=candle[3], high=candle[2], open=candle[1],
                                            close=candle[4], volume=candle[5]), candles)
    #                 log.debug ("%s"%(candles))
                    log.debug ("Historic candles for period: %s to %s num_candles: %d " % (
                        start.isoformat(), tmp_end.isoformat(), (0 if not candles else len(candles))))
                    
                    # new period, start from the (last +1)th position
                    start = tmp_end  # + timedelta(seconds = (interval//1000))
                    tmp_end = start + timedelta(seconds=td)
                    tmp_end = min(tmp_end, end)

#                     log.debug ("c: %s"%(candles))
            else:
                log.error ("Error While Retrieving Historic candles for period: %s to %s num: %d" % (
                    start.isoformat(), tmp_end.isoformat(), (0 if not candles else len(candles))))
                return None
        
        log.debug ("Retrieved Historic candles for period: %s to %s num: %d" % (
                    real_start.isoformat(), end.isoformat(), (0 if not candles_list else len(candles_list))))
    #     log.debug ("%s"%(candles_list))
        return candles_list
        
    def _normalized_order (self, order):
#         '''
#         Desc:
#          Error Handle and Normalize the order json returned by gdax
#           to return the normalized order detail back to callers
#           Handles -
#           1. Initial Order Creation/Order Query
#           2. Order Update Feed Messages
#           Ref: https://docs.gdax.com/#the-code-classprettyprintfullcode-channel
#         Sample order:
# {
#   "symbol": "BTCUSDT",
#   "orderId": 28,
#   "orderListId": -1, //Unless OCO, value will be -1
#   "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
#   "transactTime": 1507725176595,
#   "price": "1.00000000",
#   "origQty": "10.00000000",
#   "executedQty": "10.00000000",
#   "cummulativeQuoteQty": "10.00000000",
#   "status": "FILLED",
#   "timeInForce": "GTC",
#   "type": "MARKET",
#   "side": "SELL",
#   "fills": [
#     {
#       "price": "4000.00000000",
#       "qty": "1.00000000",
#       "commission": "4.00000000",
#       "commissionAsset": "USDT"
#     },
#     {
#       "price": "3999.00000000",
#       "qty": "5.00000000",
#       "commission": "19.99500000",
#       "commissionAsset": "USDT"
#     },
#     {
#       "price": "3998.00000000",
#       "qty": "2.00000000",
#       "commission": "7.99600000",
#       "commissionAsset": "USDT"
#     },   
#         Known Errors: 
#           1. {u'message': u'request timestamp expired'}
#           2. {u'message': u'Insufficient funds'}
#           3. {'status' : 'rejected', 'reject_reason': 'post-only'}
#         '''
#         error_status_codes = ['rejected']
        log.debug ("Order msg: \n%s" % (pprint.pformat(order, 4)))
        
        msg = order.get('msg')
        status = order.get('status')  or order.get('X')
        if (msg):
            log.error("FAILED Order: error msg: %s status: %s" % (msg, status))
            return None
        
        # Valid Order
        product_id = order.get('symbol')
        order_id = order.get('clientOrderId') or order.get('C') or order.get('c')
        order_type = order.get('type')

        if (status == None and (product_id != None and order_id != None)):
            log.debug ("must be an ACK for order_id (%s)" % (order_id))
            # For ACK all values might be 0, careful with calculations
            status = "NEW"
                
        if status in ['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'PENDING_CANCEL', 'REJECTED', 'EXPIRED' ]:
            if status in ["NEW", 'PARTIALLY_FILLED']:
                status_type = "open"
            elif status == 'FILLED':
                status_type = "filled"
            elif status in ['CANCELED', 'EXPIRED']:
                # order status update message
                status_type = "canceled"
            elif status == 'REJECTED':
                log.error ("order rejected msg:%s" % (order))
                return None
            else:
                log.critical ('unhandled order status(%s)' % (status))
#             order_type = order.get('order_type') #could be None
        else:
            s = "****** unknown order status: %s" % (status)
            log.critical (s)
            raise Exception (s)
            
        create_time = order.get('O') or order.get('time') or None
        update_time = order.get('updateTime') or order.get('transactTime') or order.get('T') or order.get('O') or None
        side = order.get('side') or order.get('S') or None
        
        # Money matters
        price = Decimal(order.get('price') or 0)
        request_size = Decimal(order.get('q') or order.get('origQty') or 0)
        filled_size = Decimal(order.get('z') or order.get('executedQty') or 0)
        remaining_size = Decimal(0)  # FIXME: jork:
        funds = Decimal(order.get('Z') or order.get('cummulativeQuoteQty') or 0)
        fees = Decimal(order.get('n') or 0)
        
        if price == 0 and funds != 0 and filled_size != 0 :
            price = funds / filled_size  # avg size calculation
        fills = order.get('fills')
        if fills :
            qty = 0
            comm = 0
            for fill in fills:
                qty += fill.get('qty')
                comm += fill.get('commission')
            if fees == 0:
                fees = comm
        
#         if status == "FILLED":
#             total_val = Decimal(order.get('executed_value') or 0)
#             if total_val and filled_size and not price:
#                 price = total_val/filled_size
#             if (funds == 0):
#                 funds = total_val + fees
                # log.debug ("calculated fill price: %g size: %g"%(price, filled_size))
    #         if filled_size and remaining_size:
    #             request_size = filled_size + remaining_size
                        
        if (request_size == 0):
            request_size = remaining_size + filled_size  
            
        log.debug ("price: %g fund: %g req_size: %g filled_size: %g remaining_size: %g fees: %g" % (
            price, funds, request_size, filled_size, remaining_size, fees))
        norm_order = Order (order_id, product_id, status_type, order_type=order_type,
                            side=side, request_size=request_size, filled_size=filled_size, remaining_size=remaining_size,
                             price=price, funds=funds, fees=fees, create_time=create_time, update_time=update_time)
        return norm_order        
        
    def get_product_order_book (self, product, level=1):
        log.debug ("get_product_order_book: ***********Not-Implemented******")
        return None

    def buy (self, trade_req) :
        # TODO: FIXME: Implement Market/STOP orders
        log.debug ("BUY - Placing Order on exchange --")
        
        params = {'symbol':trade_req.product, 'side' : SIDE_BUY, 'quantity':trade_req.size, "newOrderRespType": ORDER_RESP_TYPE_ACK }  # asset
        if trade_req.type == "market":
            params['type'] = ORDER_TYPE_MARKET
        else:
            params['type'] = ORDER_TYPE_LIMIT
            params['price'] = trade_req.price,  # USD
            
        if self.test_mode == False:    
            order = self.auth_client.create_order(**params)
        else:
            log.info ("placing order in test mode")            
            order = self.auth_client.create_test_order(**params)            
        return self._normalized_order (order);
    
    def sell (self, trade_req) :
        # TODO: FIXME: Implement Market/STOP orders        
        log.debug ("SELL - Placing Order on exchange --")
        params = {'symbol':trade_req.product, 'side' : SIDE_SELL, 'quantity':trade_req.size, "newOrderRespType": ORDER_RESP_TYPE_ACK  }  # asset
        if trade_req.type == "market":
            params['type'] = ORDER_TYPE_MARKET
        else:
            params['type'] = ORDER_TYPE_LIMIT
            params['price'] = trade_req.price,  # USD            
                    
        if self.test_mode == False:    
            order = self.auth_client.create_order(**params)
        else:            
            log.info ("placing order in test mode")
            order = self.auth_client.create_test_order(**params)     
        return self._normalized_order (order);
    
    def get_order (self, prod_id, order_id):
        log.debug ("GET - order (%s) " % (order_id))
        order = self.auth_client.get_order(symbol=prod_id, origClientOrderId=order_id)
        return self._normalized_order (order);
    
    def cancel_order (self, prod_id, order_id):
        log.debug ("CANCEL - order (%s) " % (order_id))
        self.auth_client.client.cancel_order(
                symbol=prod_id,
                origClientOrderId=order_id)
        return None


######### ******** MAIN ****** #########
if __name__ == '__main__':
    from market import TradeRequest
    
    print ("Testing Binance exch:")
    
    config = {"config": "config/binanceus.yml",
              'backfill': {
                  'enabled'  : True,
                  'period'   : 1,  # in Days
                  'interval' : 300,  # 300s == 5m  
                }
              }
    
    bnc = BinanceUS (config)
    
#     m = bnc.market_init('BTC-USD')

    # test historic rates
#     bnc.get_historic_rates('XLMUSDT')
#     
    # test buy order
#     tr = TradeRequest("XLMUSDT", 'BUY', 200, 200, "market", 100, 90)
#     order = bnc.buy(tr)
#     print ("buy order: %s" % (order))
#       
#     order = bnc.get_order("XLMUSDT", order.id)
#     print ("get buy order: %s" % (order))
#       
#     # test sell order
#     tr = TradeRequest("XLMUSDT", 'SELL', 200, 200, "market", 100, 90)
#     order = bnc.sell(tr)
#     print ("sell order: %s" % (order))        
#      
#     order = bnc.get_order("XLMUSDT", order.id)
#     print ("get sell order: %s" % (order))    
     
    sleep(10)
    bnc.close()
    print ("Done")
# EOF    
