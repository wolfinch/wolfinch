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
from twisted.internet import reactor

from binance.client import Client
import binance.helpers
from binance.websockets import BinanceSocketManager

from utils import getLogger, readConf
from market import Market, OHLC, feed_enQ, get_market_by_product, Order
from exchanges import Exchange


log = getLogger ('Binance')
log.setLevel(log.DEBUG)

#BINANCE CONFIG FILE
BINANCE_CONF = 'config/binance.yml'

class Binance (Exchange):
    name = "binance"
    binance_conf = {}
    binance_products = []
    binance_accounts = {}
    public_client = None
    auth_client   = None
    ws_client = None
    symbol_to_id = {}
    primary = False
    def __init__ (self, config=BINANCE_CONF, primary=False):
        log.info ("Init Binance exchange")
        
        conf = readConf (config)
        if (conf != None and len(conf)):
            self.binance_conf = conf['exchange']
        else:
            return None
        
        self.primary = primary        
        #get config
        backfill = self.binance_conf.get('backfill')
        if not backfill:
            log.fatal("Invalid Config file")
            return None
    
        for entry in backfill:
            if entry.get('enabled'):
                self.binance_conf['backfill_enabled'] = entry['enabled']
            if entry.get('period'):
                self.binance_conf['backfill_period'] = int(entry['period'])
            if entry.get('interval'):
                self.binance_conf['backfill_interval'] = str(entry['interval'])   
                    
        # for public client, no need of api key
        self.public_client = Client("", "")
        if (self.public_client) == None :
            log.critical("binance public client init failed")
            return None
        
        key = self.binance_conf.get('apiKey')
        b64secret = self.binance_conf.get('apiSecret')
        
        if ((key and b64secret ) == False):
            log.critical ("Invalid API Credentials in binance Config!! ")
            return None
        
        self.auth_client = Client(key, b64secret)
        
        if self.auth_client == None:
            log.critical("Unable to Authenticate with binance exchange. Abort!!")
            return None
            
#         global binance_products
        exch_info = self.public_client.get_exchange_info()
        products = exch_info.get("symbols")
        if (len(products) and len (self.binance_conf['products'])):
            for prod in products:
                for p in self.binance_conf['products']:
                    for k,v in p.iteritems():
#                         log.debug ("pk: %s s: %s"%(k, prod['symbol']))
                        if prod['symbol'] == k:
                            log.debug ("product found: %s p: %s"%(prod, v))
                            prod['id'] = v[0]['id']
                            prod['display_name'] = k
                            self.symbol_to_id[k] = prod['id']
                            self.binance_products.append(prod)
        
        # EXH supported in spectator mode. 
#         # Popoulate the account details for each interested currencies
#         accounts =  self.auth_client.get_account()
#         if (accounts == None):
#             log.critical("Unable to get account details!!")
#             return False
#         #log.debug ("Exchange Accounts: %s"%(pprint.pformat(accounts, 4)))
#         for account in accounts:
#             for prod in self.binance_conf['products']:
#                 for prod_id in prod.keys():
#                     currency = prod[prod_id][0]['currency']            
#                     if account['currency'] in currency:
#                         log.debug ("Interested Account Found for Currency: "+account['currency'])
#                         self.binance_accounts[account['currency']] = account
#                         break  
        
        self.ws_client = bm = BinanceSocketManager(self.public_client)
        for prod in self.get_products():
            # Start Kline socket
            backfill_interval = self.binance_conf.get('backfill_interval')
            bm.start_kline_socket(prod['symbol'], self._feed_enQ_msg, interval=backfill_interval)
        bm.start()
                
        log.info( "**CBPRO init success**\n Products: %s\n Accounts: %s"%(
                        pprint.pformat(self.binance_products, 4), pprint.pformat(self.binance_accounts, 4)))
        
    def __str__ (self):
        return "{Message: Binance Exchange }"
    ######## Feed Consume #######
    def _feed_enQ_msg (self, msg):
            log.debug("message :%s "%msg)      
            msg_type = msg.get('e') 
            symbol = msg.get("s")
            product_id = self.symbol_to_id[symbol]
            if (msg_type == 'kline'):
                log.debug ("kline")
                market = get_market_by_product (self.name, product_id)
                if (market == None):
                    log.error ("Feed Thread: Unknown market product: %s: msg %s"%(product_id, json.dumps(msg, indent=4, sort_keys=True)))
                    return
                k = msg.get('k')
                if k.get('x') == True:
                    #This kline closed, this is a candle
                    feed_enQ(market, msg)
                else:
                    # not interested
                    pass                            
            else:
                log.error ("Unknown feed. message type: %s prod: %s"%(msg_type, product_id))
            return
                
    def _binance_consume_feed (self, market, msg):
        ''' 
        Feed Call back for Binance    
        This is where we do all the useful stuff with Feed
        '''
        log.debug ("msg: %s"%msg)
#         msg_type = msg.get('e')
        now = time.time()
        k = msg.get('k')
        t = long(k.get('t'))//1000
        o = Decimal(k.get('o'))
        h = Decimal(k.get('h'))
        l = Decimal(k.get('l'))
        c = Decimal(k.get('c'))
        v = Decimal(k.get('v'))
        
#         if now >= market.cur_candle_time + interval:
            # close the current candle period and start a new candle period
        candle = OHLC(long(t), o, h, l, c, v)
        log.debug ("New candle identified %s"%(candle))        
        market.O = market.V = market.H = market.L = 0
        market.cur_candle_time = now
        market.add_new_candle (candle)
        
        #TODO: FIXME: jork: might need to rate-limit the logic here after
        market.set_market_rate (c)
        market.update_market_states()        
            
    #### Feed consume done #####    
    
    #TODO: FIXME: Spectator mode, make full operational    
    def market_init (self, product):
#         usd_acc = self.binance_accounts['USD']
#         crypto_acc = self.binance_accounts.get(product['base_currency'])
#         if (usd_acc == None or crypto_acc == None): 
#             log.error ("No account available for product: %s"%(product['id']))
#             return None
        #Setup the initial params
#         log.debug ("product: %s"%product)
        market = Market(product=product, exchange=self)    
        market.fund.set_initial_value(Decimal(0))#usd_acc['available']))
        market.fund.set_hold_value(Decimal(0))#usd_acc['hold']))
        market.fund.set_fund_liquidity_percent(10)       #### Limit the fund to 10%
        market.fund.set_max_per_buy_fund_value(100)
        market.asset.set_initial_size(Decimal(0)) #crypto_acc['available']))
        market.asset.set_hold_size(0) #Decimal(crypto_acc['hold']))
    
        ## Feed Cb
        market.consume_feed = self._binance_consume_feed
        
        ## Init Exchange specific private state variables
        market.O = market.H = market.L = market.C = market.V = 0
        log.info ("Market init complete: %s"%(product['id']))
        
        #set whether primary or secondary
        market.primary = self.primary
        
        return market
    def close (self):
        log.debug("Closing exchange...")    
#         global self.ws_client
        if (self.ws_client):
            log.debug("Closing WebSocket Client")
            self.ws_client.close ()
            self.ws_client.join(1)
            reactor.stop()
            log.debug("Closed websockets")
    def get_products (self):
        log.debug ("products num %d"%(len(self.binance_products)))
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
        #Max Candles in one call
        epoch = datetime.utcfromtimestamp(0)
        max_candles = 200
        candles_list = []
        
        #get config
        enabled = self.binance_conf.get('backfill_enabled')
        period = int(self.binance_conf.get('backfill_period'))
        interval_str = self.binance_conf.get('backfill_interval')
        
        interval = binance.helpers.interval_to_milliseconds(interval_str)
        if (interval == None):
            log.error ("Invalid Interval - %s"%interval_str)
        
        product = None
        for p in self.get_products():
            if p['id'] == product_id:
                product = p
        
        if product is None:
            log.error ("Invalid Product Id: %s"%product_id)
            return None
        
        if not enabled:
            log.debug ("Historical data retrieval not enabled")
            return None
    
        if not end:
            # if no end, use current time
            end = datetime.now()
             
        if not start:
            # if no start given, use the config
            real_start = start = end - timedelta(days = period) - timedelta(seconds = interval//1000)
        else:
            real_start = start
        
        log.debug ("Retrieving Historic candles for period: %s to %s"%(
                    real_start.isoformat(), end.isoformat()))
        
        td = max_candles*interval//1000
        tmp_end = start + timedelta(seconds = td)
        tmp_end = min(tmp_end, end)
        count = 0
        while (start < end):
            ## looks like there is a rate=limiting in force, we will have to slow down
            count += 1
            if (count > 3):
                #rate-limiting
                count = 0
                sleep (2)
            
            start_ts = int((start - epoch).total_seconds() * 1000.0)
            end_ts = int((tmp_end - epoch).total_seconds() * 1000.0)
            
            log.debug ("Start: %s end: %s"%(start_ts, end_ts))
            candles = self.public_client.get_klines (
                symbol=product['symbol'],
                interval=Client.KLINE_INTERVAL_5MINUTE,
                limit=max_candles,
                startTime=start_ts,
                endTime=end_ts
            )
            if candles:
                if isinstance(candles, dict):
                    ## Error Case
                    err_msg = candles.get('message')
                    if (err_msg):
                        log.error ("Error while retrieving Historic rates: msg: %s\n will retry.."%(err_msg))
                else:
                    #candles are of struct [[time, o, h, l,c, V]]
                    candles_list += map(
                        lambda candle: OHLC(time=long(candle[0])//1000, 
                                            low=candle[3], high=candle[2], open=candle[1], 
                                            close=candle[4], volume=candle[5]), candles)
    #                 log.debug ("%s"%(candles))
                    log.debug ("Historic candles for period: %s to %s num_candles: %d "%(
                        start.isoformat(), tmp_end.isoformat(), (0 if not candles else len(candles))))
                    
                    # new period, start from the (last +1)th position
                    start = tmp_end #+ timedelta(seconds = (interval//1000))
                    tmp_end = start + timedelta(seconds = td)
                    tmp_end = min(tmp_end, end)

#                     log.debug ("c: %s"%(candles))
            else:
                log.error ("Error While Retrieving Historic candles for period: %s to %s num: %d"%(
                    start.isoformat(), tmp_end.isoformat(), (0 if not candles else len(candles))))
                return None
        
        log.debug ("Retrieved Historic candles for period: %s to %s num: %d"%(
                    real_start.isoformat(), end.isoformat(), (0 if not candles_list else len(candles_list))))
    #     log.debug ("%s"%(candles_list))
        return candles_list
        
    def get_product_order_book (self, product, level = 1):
        log.error ("***********Not-Implemented******")
        return None
    
    def buy (self):
        log.error ("***********Not-Implemented******")
        return None
    def sell (self):
        log.error ("***********Not-Implemented******")
        return None
    def get_order (self):
        log.error ("***********Not-Implemented******")
        return None
    def cancel_order (self):
        log.error ("***********Not-Implemented******")
        return None

######### ******** MAIN ****** #########
if __name__ == '__main__':
    
    print ("Testing Binance exch:")
    
    bnc = Binance ()
    
#     m = bnc.market_init('BTC-USD')
    
    bnc.get_historic_rates('BTC-USD')
    
    sleep(20)
    bnc.close()
    print ("Done")
#EOF    
