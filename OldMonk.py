#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Main File implements Bot
# Copyright 2019, OldMonk Bot. All Rights Reserved.
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

from __future__ import print_function
import time
import pkgutil
import pprint
import sys
from decimal import *
import argparse

import sims
from exchanges import exchanges
from market import *
from utils import getLogger
import db
from utils.readconf import readConf
from dateparser import conf
import stats

log = getLogger ('OldMonk')
log.setLevel(log.CRITICAL)

# Global Variables
decisionConfig = {}
OldMonkConfig = None
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
    market_setup(decisionConfig)
    
    #5. start stats thread
    stats.start()
    
def OldMonk_end():
    log.info ("Finalizing OldMonk")
    close_exchanges ()
    
    # stop stats thread
    stats.stop()
    
def init_exchanges ():
    global exchange_list, OldMonkConfig
    
    #init exchanges 
    for exch_cls in exchanges:
        log.debug ("Initializing exchange (%s)"%(exch_cls.name))
        for exch in OldMonkConfig['exchanges']:
            for name,v in exch.iteritems():
                if name.lower() == exch_cls.name.lower():
                    role = v['role']
                    cfg = v['config']
                    log.debug ("initializing exchange(%s)"%name)
                    exch_obj = exch_cls(config=cfg, primary=(role == 'primary'))
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
#         log.critical("Current (%d) Sleep time left:%s"%(cur_time, str(sleep_time)))         
        # check for the msg in the feed Q and process, with timeout
        msg = feed_deQ(sleep_time) 
#         log.critical("Current (%d)"%(time.time()))
        while (msg != None):
            feed_Q_process_msg (msg)
            msg = feed_deQ(0)        
        for market in get_market_list():
            process_market (market)
        '''Make sure each iteration take exactly LOOP_DELAY time'''
        sleep_time = (MAIN_TICK_DELAY - (time.time() - cur_time))
#         if sleep_time < 0 :
#             log.critical ("******* TIMING SKEWED (%f) ******"%(sleep_time))
        sleep_time  = 0 if (sleep_time < 0) else sleep_time     
    #end While(true)
    
def process_market (market):
    """ 
    processing routine for one exchange
    """
    log.info ("processing Market: exchange (%s) product: %s"%( market.exchange_name, market.name))
    market.update_market_states()
    
    # Trade only on primary markets
    if market.primary is True and market.new_candle is True:
        signal = market.generate_trade_signal ()
        market.consume_trade_signal (signal)
        if (sims.simulator_on):
            sims.market_simulator_run (market)
    
def clean_states ():
    log.info ("Clearing Db")
    db.clear_db()
    stats.clear_stats()
    
def load_config (cfg_file):
    global OldMonkConfig
    global decisionConfig
    OldMonkConfig = readConf(cfg_file)
    if not conf:
        return False
    
    log.debug ("cfg: %s"%OldMonkConfig)
    # sanitize the config
    for k,v in OldMonkConfig.iteritems():
        if k == 'exchanges':
            prim = False
            for exch in v:
                for ex_k, ex_v in exch.iteritems():
                    log.debug ("processing exch: %s"%ex_k)
                    role = ex_v.get('role')
                    if role == 'primary':
                        if prim == True:
                            print ("more than one primary exchange not supported")
                            return False
                        else:
                            prim = True
            if prim == False:
                print ("No primary exchange configured!!")
                return False
        elif k == 'decision':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'model':
                    decisionConfig ['model_type'] = ex_v
                elif ex_k == 'config':
                    decisionConfig ['model_config'] = ex_v     
        elif k == 'simulator':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    if ex_v == True:
                        log.debug ("simulator enabled")
                        sims.simulator_on = True
                    else:
                        log.debug ("simulator disabled")
                        sims.simulator_on = False
                elif ex_k == 'backtesting':
                    if ex_v == True:
                        log.debug ("backtesting enabled")
                        sims.backtesting_on = True
                    else:
                        log.debug ("backtesting disabled")       
                        sims.backtesting_on = False
                
#                 print ("v: %s"%str(ex_k))
#     exit(1)
    log.debug ("config loaded successfully!")
    return True
        
def arg_parse ():
    parser = argparse.ArgumentParser(description='OldMonk Auto Trading Bot')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--clean", help='Clean states,dbs and exit. Clear all the existing states', action='store_true')
    parser.add_argument("--config", help='OldMonk Global config file')
    parser.add_argument("--backtesting", help='do backtesting', action='store_true')
    parser.add_argument("--import_only", help='do import only', action='store_true')
    
    args = parser.parse_args()
    
    if (args.clean):
        clean_states ()
        exit (0)
        
    if (args.import_only):              
        log.debug ("import_only enabled")       
        sims.import_only = True
    else:
        log.debug ("import_only disabled")       
        sims.import_only = False          
        
    if (args.backtesting):              
        log.debug ("backtesting enabled")       
        sims.backtesting_on = True
    else:
        log.debug ("backtesting disabled")       
        sims.backtesting_on = False        
                 
    if (args.config):
        log.debug ("config file: %s"%args.config)
        if False == load_config (args.config):
            log.critical ("Config parse error!!")
            parser.print_help()
            exit(1)
        else:
            log.debug ("config loaded successfully!")
#             exit (0)
    else:
        parser.print_help()
        exit(1)
    
#     log.debug("sims.backtesting_on: %d"%(sims.backtesting_on))
#     exit(1)
    
######### ******** MAIN ****** #########
if __name__ == '__main__':
    
    arg_parse()
    
    getcontext().prec = 8 #decimal precision
    
    print("Starting OldMonk..")
    
    try:
        OldMonk_init()
        
        if sims.import_only:
            log.info ("import only")
            raise SystemExit
               
        if (sims.backtesting_on):
            sims.market_backtesting_run ()
            raise SystemExit
        else:
            log.debug ("Starting Main forever loop")
            oldmonk_main ()
    except (KeyboardInterrupt, SystemExit):
        OldMonk_end()
        sys.exit()
    except:
        print ("Unexpected error: ",sys.exc_info())
        OldMonk_end()
        raise
    #'''Not supposed to reach here'''
    print("\nOldMonk end")
    

#EOF
