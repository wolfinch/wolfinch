#! /usr/bin/env python

'''
 SkateBot Auto trading Bot
 Desc: Main File implements Bot
 (c) Joshith Rayaroth Koderi
'''
import time
import pkgutil
import pprint
from collections import namedtuple

from utils import logger
import exchanges
from market import *

log = logger.getLogger ('SkateBot')

exchange_list = []
SkateBot_market_list = []
TICK_DELAY    = 20        # 20 Sec

def SkateBot_init():
    init_exchanges()
    market_init ()    
def init_exchanges ():
    global exchange_list
    #init exchanges 
    for importer, modname, ispkg in pkgutil.iter_modules(exchanges.__path__):
        if ispkg == True:
            log.debug ("Initializing exchange (%s)"%(modname))
            exchange = getattr(exchanges, modname)
            if (exchange.init() == True):
                exchange_list.append(exchange)
                #Market init
            else:
                log.critical (" Exchange \"%s\" init failed "%modname)
def market_init ():
    '''
    Initialize per exchange, per product data.
    This is where we want to keep all the run stats
    {
     product_id :
     product_name: 
     exchange_name:
     fund {
     initial_value:   < Initial fund value >
     current_value:
     current_hold_value
     total_traded_value:
     current_realized_profit:
     current_unrealized_profit
     total_profit:
     fund_liquidity_percent: <% of total initial fund allowed to use>     
     max_per_buy_fund_value:
     }
     crypto {
     initial_size:
     current_size:
     current_hold_size:
     current_avg_value:
     total_traded_size:
     }
     orders {
     total_order_num
     open_buy_orders_db: <dict>
     open_sell_orders_db: <dict>
     traded_buy_orders_db:
     traded_sell_orders_db:
     }
    } 
    '''
    for exchange in exchange_list:
        for product in exchange.get_products():
            market = exchange.market_init (exchange, product)
            if (market == None):
                log.critical ("Market Init Failed for exchange: %s product: %s"%(exchange.__name__, product['id']))
            else:
                SkateBot_market_list.append(market)
                            
def skatebot_main ():
    """
    Main loop for Skatebot
    """
    while (True) : 
        cur_time = time.time()
        for market in SkateBot_market_list:
            process_market (market)
        '''Make sure each iteration take exactly LOOP_DELAY time'''
        sleep_time = (TICK_DELAY - (time.time() - cur_time))
        sleep_time  = 0 if (sleep_time < 0) else sleep_time
        log.debug("Current Sleep time left:"+str(sleep_time))          
        time.sleep(sleep_time)          
    #end While(true)
def process_market (market):
    """ 
    processing routine for one exchange
    """
    log.info ("processing Market: exchange (%s) product: %s"%( market.exchange_name, market.name))
    update_market_states(market)
    signal = generate_trade_signal (market)
    consume_trade_signal (market, signal)

######### ******** MAIN ****** #########
if __name__ == '__main__':
    log.info("Starting SkateBot..")
    SkateBot_init()
    log.debug ("Starting Main Loop")
    skatebot_main ()
    
    #'''Not supposed to reach here'''
    log.info("SkateBot end")
    

#EOF