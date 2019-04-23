#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Main File implements Bot
# Copyright 2018, Joshith Rayaroth Koderi. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import pkgutil
import pprint
import sys
from decimal import *
import argparse

import sims
from exchanges import exchanges
from market import *
from utils import *
import db

log = getLogger ('OldMonk')
log.setLevel(log.CRITICAL)

# Global Variables
exchange_list = []
MAIN_TICK_DELAY    = 10        # 20 Sec

def OldMonk_init():
    global exchange_list
    
    #1. Retrieve states back from Db
    db.init_order_db(Order)
    
    #2. Init Exchanges
    init_exchanges()
    
    #3. Init markets
    market_init (exchange_list)
    
    #4. Setup markets
    market_setup()
    
def OldMonk_end():
    log.info ("Finalizing OldMonk")
    close_exchanges ()
    
def init_exchanges ():
    global exchange_list
    #init exchanges 
    for exch_cls in exchanges:
        log.debug ("Initializing exchange (%s)"%(exch_cls.name))
        exch_obj = exch_cls()
        if (exch_obj != None):
            exchange_list.append(exch_obj)
            #Market init
        else:
            log.critical (" Exchange \"%s\" init failed "%exch_cls.name)
                
def close_exchanges():
    global exchange_list
    #init exchanges 
    for exchange in exchange_list:
            log.info ("Closing exchange (%s)"%(exchange.name))
            exchange.close()    

def oldmonk_main ():
    """
    Main Function for OldMonk
    """
    sleep_time = MAIN_TICK_DELAY
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
        sleep_time = (MAIN_TICK_DELAY - (time.time() - cur_time))
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
    
def clean_states ():
    log.info ("Clearing Db")
    db.clear_db()
    
        
def arg_parse ():
    parser = argparse.ArgumentParser(description='OldMonk Auto Trading Bot')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--clean", help='Start Clean. Clear all the existing states', action='store_true')
    
    args = parser.parse_args()
    
    if (args.clean):
        clean_states ()
        exit ()
    
######### ******** MAIN ****** #########
if __name__ == '__main__':
    
    arg_parse()
    
    getcontext().prec = 8 #decimal precision
    
    print("Starting OldMonk..")
    
    try:
        OldMonk_init()
        log.debug ("Starting Main Loop")
        oldmonk_main ()
    except (KeyboardInterrupt, SystemExit):
        OldMonk_end()
        sys.exit()
    except:
        print ("Unexpected error: ",sys.exc_info())
        OldMonk_end()
        raise
    #'''Not supposed to reach here'''
    print("OldMonk end")
    

#EOF
