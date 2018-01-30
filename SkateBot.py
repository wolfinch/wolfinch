#! /usr/bin/env python

# '''
#  SkateBot Auto trading Bot
#  Desc: Main File implements Bot
#  (c) Joshith Rayaroth Koderi
# '''

import time
import pkgutil
import pprint
from decimal import *

import sims
import exchanges
from market import *
from utils import *

log = getLogger ('SkateBot')
log.setLevel(log.CRITICAL)

# Global Variables
exchange_list = []
TICK_DELAY    = 10        # 20 Sec

def SkateBot_init():
    global SkateBot_market_list, exchange_list
    init_exchanges()
    market_init (exchange_list)    
    
def SkateBot_end():
    log.info ("Finalizing SkateBot")
    close_exchanges ()
    
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
                
def close_exchanges():
    global exchange_list
    #init exchanges 
    for exchange in exchange_list:
            log.info ("Closing exchange (%s)"%(exchange.__name__))
            exchange.close()    

def skatebot_main ():
    """
    Main Function for Skatebot
    """
    sleep_time = TICK_DELAY
    while (True) : 
        cur_time = time.time()
        log.debug("Current Sleep time left:"+str(sleep_time))          
        #time.sleep(sleep_time)             
        # check for the msg in the feed Q and process, with timeout
        msg = feed_deQ(sleep_time) 
        while (msg != None):
            feed_Q_process_msg (msg)
            msg = feed_deQ(0)        
        for market in get_market_list():
            process_market (market)
        '''Make sure each iteration take exactly LOOP_DELAY time'''
        sleep_time = (TICK_DELAY - (time.time() - cur_time))
        sleep_time  = 0 if (sleep_time < 0) else sleep_time     
    #end While(true)
    
def process_market (market):
    """ 
    processing routine for one exchange
    """
    log.info ("processing Market: exchange (%s) product: %s"%( market.exchange_name, market.name))
    market.update_market_states()
    signal = market.generate_trade_signal ()
    market.consume_trade_signal (signal)
    if (sims.simulator_on):
        sims.market_simulator_run (market)
    
######### ******** MAIN ****** #########
if __name__ == '__main__':
    getcontext().prec = 8 #decimal precision
    print("Starting SkateBot..")
    try:
        SkateBot_init()
        log.debug ("Starting Main Loop")
        skatebot_main ()
    except KeyboardInterrupt:
        SkateBot_end()
    #'''Not supposed to reach here'''
    print("SkateBot end")
    

#EOF