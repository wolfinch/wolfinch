#! /usr/bin/env python3
# '''
#  Wolfinch Auto trading Bot
#  Desc: Robinhood exchange interactions for Wolfinch
#
#  Copyright: (c) 2017-2020 Joshith Rayaroth Koderi
#  This file is part of Wolfinch.
# 
#  Wolfinch is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  Wolfinch is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with Wolfinch.  If not, see <https://www.gnu.org/licenses/>.
# '''

import json
import pprint
from datetime import datetime, timedelta
from time import sleep
import time
from dateutil.tz import tzlocal, tzutc
from twisted.internet import reactor

import pyrh

# from .robinhood.enums import *
# from .robinhood.client import Client
# from . import robinhood
# from .robinhood.websockets import RobinhoodSocketManager

from utils import getLogger, readConf
from market import Market, OHLC, feed_enQ, get_market_by_product, Order
from exchanges import Exchange

log = getLogger ('Robinhood')
log.setLevel(log.DEBUG)

# ROBINHOOD CONFIG FILE
ROBINHOOD_CONF = 'config/robinhood.yml'
RBH_INTERVAL_MAPPING = {300 :'5m', 600: '10m'}


class Robinhood (Exchange):
    name = "robinhood"
    robinhood_conf = {}
    robinhood_products = []
    robinhood_accounts = {}
#     public_client = None
    auth_client = None
#     ws_client = None
#     ws_auth_client = None
#     symbol_to_id = {}
    primary = False

    def __init__(self, config, primary=False):
        log.info ("Init Robinhood exchange")
        self.symbols = {}
        exch_cfg_file = config['config']
        
        conf = readConf (exch_cfg_file)
        if (conf != None and len(conf)):
            self.robinhood_conf = conf['exchange']
        else:
            return None
        
        self.primary = True if primary else False
        # get config
        if config.get('candle_interval'):
            # map interval in to robinhood format
            interval = RBH_INTERVAL_MAPPING[int(config['candle_interval']) ]
            self.robinhood_conf['backfill_interval'] =  interval
            self.candle_interval = int(config['candle_interval'])        
                
        # get config
        backfill = config.get('backfill')
        if not backfill:
            log.fatal("Invalid backfill config")            
            return None
    
        if backfill.get('enabled'):
            self.robinhood_conf['backfill_enabled'] = backfill['enabled']
        if backfill.get('period'):
            self.robinhood_conf['backfill_period'] = int(backfill['period'])

        
        # for public client, no need of api key
#         self.public_client =  Robinhood()
#         if (self.public_client) == None :
#             log.critical("robinhood public client init failed")
#             return None
        
        #get data from exch conf
        self.user = self.robinhood_conf.get('user')
        self.password = self.robinhood_conf.get('password')
        self.mfa_key = self.robinhood_conf.get('MFAcode')
        
        if ((self.user and self.password) == False):
            log.critical ("Invalid API Credentials in robinhood Config!! ")
            return None
        
        try :
            self.auth_client = pyrh.Robinhood()
            if self.auth_client.login(username=self.user, password=self.password, qr_code=self.mfa_key) == False:
                log.critical("Unable to Authenticate with robinhood exchange. Abort!!")
                raise Exception("login failed")
        except Exception as e:
            log.critical ("exception while logging in e:%s"%(e))        
            raise e
        
#         global robinhood_products
#         exch_info = self.public_client.get_exchange_info()
#         serverTime = int(exch_info['serverTime'])
#         localTime = int(time.time() * 1000)
#         self.timeOffset = (serverTime - localTime) // 1000
#         # if time diff is less the 5s, ignore. 
#         if abs(self.timeOffset) < 5: 
#             self.timeOffset = 0
#    
#         log.info ("servertime: %d localtime: %d offset: %d" % (serverTime, localTime, self.timeOffset))
        
#         self.robinhood_conf['products'] = []
#         for p in config['products']:
#             # add the product ids
#             self.robinhood_conf['products'] += p.keys()
                    
        portforlio = self.auth_client.portfolios()
        log.info ("products: %s" % (pprint.pformat(portforlio, 4)))
                
#         if (len(products) and len (self.robinhood_conf['products'])):
#             for prod in products:
#                 for p in self.robinhood_conf['products']:
#                     for k, v in p.items():
# #                         log.debug ("pk: %s s: %s"%(k, prod['symbol']))
#                         if prod['symbol'] == k:
#                             log.debug ("product found: %s v: %s" % (prod, v))
#                             prod['id'] = v['id']
#                             prod['display_name'] = k
#                             self.symbol_to_id[k] = prod['id']
#                             prod ['asset_type'] = prod['baseAsset']
#                             prod ['fund_type'] = prod['quoteAsset']
#                                                   
#                             self.robinhood_products.append(prod)
        
        # EXH supported in spectator mode. 
        # Popoulate the account details for each interested currencies
        accounts = self.auth_client.get_account()
        if (accounts == None):
            log.critical("Unable to get account details!!")
            return False
        log.debug ("Exchange Accounts: %s" % (pprint.pformat(accounts, 4)))
#         balances = accounts ['balances']
#         for balance in balances:
# #             log.debug ("balance: %s"%(balance))
#             for prod in self.robinhood_products:
#                 log.debug ("prod_id: %s" % (prod['id']))               
#                 if balance['asset'] in [prod ['asset_type'], prod ['fund_type']]:
#                     log.debug ("Interested Account Found for Currency: " + balance['asset'])
#                     self.robinhood_accounts[balance['asset']] = balance
#                     break  
        
        ### Start WebSocket Streams ###
#         self.ws_client = bm = RobinhoodSocketManager(self.public_client)
#         symbol_list = []
#         for prod in self.get_products():
#             # Start Kline socket
# #             backfill_interval = self.robinhood_conf.get('backfill_interval')
# #             bm.start_kline_socket(prod['symbol'], self._feed_enQ_msg, interval=backfill_interval)
# #             bm.start_aggtrade_socket(prod['symbol'], self._feed_enQ_msg)
#             symbol_list.append(prod['symbol'].lower()+"@trade")
#             
#         if len(symbol_list):
#             #start mux ws socket now
#             log.info ("starting mux ws sockets for syms: %s"%(symbol_list))
#             bm.start_multiplex_socket(symbol_list, self._feed_enQ_msg)
#             
#         self.ws_auth_client = bm_auth = RobinhoodSocketManager(self.auth_client)
#         # Start user socket for interested symbols
#         log.info ("starting user sockets")
#         bm_auth.start_user_socket(self._feed_enQ_msg)            
# 
#         bm.start()
#         bm_auth.start()
        
        log.info("**Robinhood init success**\n Products: %s\n Accounts: %s" % (
                        pprint.pformat(self.robinhood_products, 4), pprint.pformat(self.robinhood_accounts, 4)))
        
    def __str__ (self):
        return "{Message: Robinhood Exchange }"
       
            
    def market_init (self, market):
#         global ws_client
        usd_acc = self.robinhood_accounts[market.get_fund_type()]
        asset_acc = self.robinhood_accounts.get(market.get_asset_type())
        if (usd_acc == None or asset_acc == None): 
            log.error ("No account available for product: %s"%(market.product_id))
            return None
        
#         #Setup the initial params
        market.fund.set_initial_value(float(usd_acc['free']))
        market.fund.set_hold_value(float(usd_acc['locked']))
        market.asset.set_initial_size(float( asset_acc['free']))
        market.asset.set_hold_size( float(asset_acc['locked']))
        
        ## Feed Cb
        market.register_feed_processor(self._robinhood_consume_feed)
        
        ## Init Exchange specific private state variables
        market.set_candle_interval (self.candle_interval)
        
#         #set whether primary or secondary
        log.info ("Market init complete: %s" % (market.product_id))
                
        return market

    def close (self):
        log.debug("Closing exchange...")
# #         global self.ws_client
#         if (self.ws_client):
#             log.debug("Closing WebSocket Client")
#             self.ws_client.close ()
#             self.ws_client.join(1)
#         if (self.ws_auth_client):
#             log.debug("Closing WebSocket Auth Client")
#             self.ws_auth_client.close ()
#             self.ws_auth_client.join(1)
        
        #log out now. 
        self.auth_client.logout()
        log.debug("Closed websockets")

    def get_products (self):
        log.debug ("products num %d" % (len(self.robinhood_products)))
        return self.robinhood_products    

    def get_accounts (self):
    #     log.debug (pprint.pformat(self.robinhood_accounts))
        log.debug ("get accounts")
        return self.robinhood_accounts    

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
        enabled = self.robinhood_conf.get('backfill_enabled')
        period = int(self.robinhood_conf.get('backfill_period'))
        interval_str = self.robinhood_conf.get('backfill_interval')
        
        interval = robinhood.helpers.interval_to_milliseconds(interval_str)
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
                    candles_list += [OHLC(time=int(candle[6] + 1) // 1000,
                                            low=candle[3], high=candle[2], open=candle[1],
                                            close=candle[4], volume=candle[5]) for candle in candles]
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
        product_id = order.get('symbol') or order.get("s")
        order_id = order.get('clientOrderId') or order.get('c')
        order_type = order.get('type') or order.get("o")
        
        if order_type == "MARKET":
            order_type = "market"
        elif order_type == "LIMIT":
            order_type = 'limit'

        if (status == None and (product_id != None and order_id != None)):
            log.debug ("must be an ACK for order_id (%s)" % (order_id))
            # For ACK all values might be 0, careful with calculations
            status = "NEW"
                
        if status in ['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'PENDING_CANCEL', 'REJECTED', 'EXPIRED' ]:
            if status == "NEW":
                status_type = "open"
            elif status == 'FILLED':
                status_type = "filled"
            elif status in ['CANCELED', 'EXPIRED']:
                # order status update message
                status_type = "canceled"
            elif status == 'REJECTED':
                log.error ("order rejected msg:%s" % (order))
                return None
            else: #, 'PARTIALLY_FILLED'
                log.critical ('unhandled order status(%s)' % (status))
                return None
#             order_type = order.get('order_type') #could be None
        else:
            s = "****** unknown order status: %s" % (status)
            log.critical (s)
            raise Exception (s)
            
        create_time = order.get('O') or order.get('time') 
        if create_time:
            create_time = datetime.utcfromtimestamp(int(create_time)/1000).replace(tzinfo=tzutc()).astimezone(tzlocal()).isoformat()
#         else:
#             create_time = datetime.now().isoformat()
        update_time = order.get('updateTime') or order.get('transactTime') or order.get('T') or order.get('O') or None
        if update_time:
            update_time = datetime.utcfromtimestamp(int(update_time)/1000).replace(tzinfo=tzutc()).astimezone(tzlocal()).isoformat()
        else:
            update_time = datetime.now().isoformat()
                    
        side = order.get('side') or order.get('S') or None
        if side == None:
            log.critical("unable to get order side %s(%s)"%(product_id, order_id))
            raise Exception ("unable to get order side")
        elif side == 'BUY':
            side = 'buy'
        elif side == 'SELL':
            side = 'sell'
        
        # Money matters
        price = float(order.get('price') or 0)
        request_size = float(order.get('q') or order.get('origQty') or 0)
        filled_size = float(order.get('z') or order.get('executedQty') or 0)
        remaining_size = float(0)  # FIXME: jork:
        funds = float(order.get('Z') or order.get('cummulativeQuoteQty') or 0)
        fees = float(order.get('n') or 0)
        
        if price == 0 and funds != 0 and filled_size != 0 :
            price = funds / filled_size  # avg size calculation
        fills = float(order.get('fills') or 0)
        if fills :
            qty = float(0.0)
            comm = float(0.0)
            for fill in fills:
                qty += float(fill.get('qty') or 0)
                comm += float(fill.get('commission') or 0)
            if fees == 0:
                fees = float(comm)
        
#         if status == "FILLED":
#             total_val = float(order.get('executed_value') or 0)
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
        
        try:
            if self.test_mode == False:    
                order = self.auth_client.create_order(**params)
            else:
                log.info ("placing order in test mode")            
                order = self.auth_client.create_test_order(**params)
        except Exception as e:
            log.error ("exception while placing order - %s"%(e))
            return None
        order["side"] = 'buy'     
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
                    
        try:
            if self.test_mode == False:    
                order = self.auth_client.create_order(**params)
            else:            
                log.info ("placing order in test mode")
                order = self.auth_client.create_test_order(**params)     
        except Exception as e:
            log.error ("exception while placing order - %s"%(e))
            return None            
        order["side"] = 'sell'
        return self._normalized_order (order);
    
    def get_order (self, prod_id, order_id):
        log.debug ("GET - order (%s) " % (order_id))
        try:
            order = self.auth_client.get_order(symbol=prod_id, origClientOrderId=order_id)
        except Exception as e:
            log.error ("exception while placing order - %s"%(e))
            return None        
        return self._normalized_order (order);
    
    def cancel_order (self, prod_id, order_id):
        log.debug ("CANCEL - order (%s) " % (order_id))
        self.auth_client.client.cancel_order(
                symbol=prod_id,
                origClientOrderId=order_id)
        return None
    def _fetch_json_by_url(self, url):
        return self.auth_client.get_url(url)

    def _get_symbol_from_instrument(self, instr):
        i_id = instr.rstrip('/').split('/')[-1]
        sym = self.symbols.get(i_id)
        if sym:
            log.debug ("found cached symbol for id: %s symbol: %s"%(i_id, sym['symbol']))
            return sym
        else:
            sym = self._fetch_json_by_url(instr)
            if sym :
                log.error("got symbol for id %s symbol: %s"%(i_id, sym))   
                self.symbols[i_id] = sym
                return sym
            else:
                log.error("unable to get symbol for id %s"%(i_id))
    def get_all_history_orders(self):
        orders = []
        past_orders = self.auth_client.order_history()
        orders.extend(past_orders['results'])
        log.info("%d order fetched first page"%(len(orders)))    
        while past_orders['next']:
            next_url = past_orders['next']
            past_orders = self._fetch_json_by_url(next_url)
            orders.extend(past_orders['results'])
        log.info("%d  order fetched"%(len(orders)))
        for order in orders:
            instrument = order['instrument']
            symbol = self._get_symbol_from_instrument(instrument)
            if symbol:
                order['symbol'] = symbol['symbol']
                order['bloomberg_unique'] = symbol['bloomberg_unique']
            else:
                log.error ('unable to get symbol for instrument')  
        return orders

    def get_all_history_options_orders(self):
    
        options_orders = []
        past_options_orders = self.auth_client.options_order_history()
        options_orders.extend(past_options_orders['results'])
    
        while past_options_orders['next']:
            # print("{} order fetched".format(len(orders)))
            next_url = past_options_orders['next']
            past_options_orders = fetch_json_by_url(my_trader, next_url)
            options_orders.extend(past_options_orders['results'])
        # print("{} order fetched".format(len(orders)))
        
        options_orders_cleaned = []
        
        for each in options_orders:
            if float(each['processed_premium']) < 1:
                continue
            else:
    #             print(each['chain_symbol'])
    #             print(each['processed_premium'])
    #             print(each['created_at'])
    #             print(each['legs'][0]['position_effect'])
    #             print("~~~")
                if each['legs'][0]['position_effect'] == 'open':
                    value = round(float(each['processed_premium']), 2)*-1
                else:
                    value = round(float(each['processed_premium']), 2)
                    
                one_order = [pd.to_datetime(each['created_at']), each['chain_symbol'], value, each['legs'][0]['position_effect']]
                options_orders_cleaned.append(one_order)
        
        df_options_orders_cleaned = pd.DataFrame(options_orders_cleaned)
        df_options_orders_cleaned.columns = ['date', 'ticker', 'value', 'position_effect']
        df_options_orders_cleaned = df_options_orders_cleaned.sort_values('date')
        df_options_orders_cleaned = df_options_orders_cleaned.set_index('date')
    
        return df_options_orders_cleaned

######### ******** MAIN ****** #########
if __name__ == '__main__':
    from market import TradeRequest
    
    print ("Testing Robinhood exch:")
    
    config = {"config": "config/robinhood.yml",
              'backfill': {
                  'enabled'  : True,
                  'period'   : 1,  # in Days
                  'interval' : 300,  # 300s == 5m  
                }
              }
    
    rbh = Robinhood (config)
    
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
    
    rbh.auth_client.print_quote("AAPL")
    orders = rbh.get_all_history_orders()
    
    print ("orders: %s"%orders)
    sleep(10)
    rbh.close()
    print ("Done")
# EOF    
