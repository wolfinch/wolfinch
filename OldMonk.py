#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Main File implements Bot
# Copyright 2019, Joshith Rayaroth Koderi. All Rights Reserved.
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
import sys
import argparse
from decimal import getcontext

import sims
import exchanges
from market import market_init, market_setup, get_market_list, feed_Q_process_msg, feed_deQ, Order
from utils import getLogger
import db
from utils.readconf import readConf
from dateparser import conf
import stats

log = getLogger ('OldMonk')
log.setLevel(log.INFO)

# Global Config 
OldMonkConfig = None

decisionConfig = {}
tradingConfig = {"stop_loss_enabled": False, "stop_loss_smart_rate": False, 'stop_loss_rate': 0,
                 "take_profit_enabled": False, 'take_profit_rate': 0} 

# global Variables
MAIN_TICK_DELAY    = 0.500 #500 milli

def OldMonk_init(decisionConfig, tradingConfig):
    
    #1. Retrieve states back from Db
#     db.init_order_db(Order)
    
    #2. Init Exchanges
    exchanges.init_exchanges(OldMonkConfig)
    
    #3. Init markets
    market_init (exchanges.exchange_list, decisionConfig, tradingConfig)
    
    #4. Setup markets
    market_setup()
    
    #5. start stats thread
    stats.start()
    
def OldMonk_end():
    log.info ("Finalizing OldMonk")
    exchanges.close_exchanges ()
    
    # stop stats thread
    log.info ("waiting to stop stats thread")
    stats.stop()
    log.info ("all cleanup done.")
    

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
    log.debug ("processing Market: exchange (%s) product: %s"%( market.exchange_name, market.name))
    market.update_market_states()
    
    # Trade only on primary markets
    if market.primary is True and market.new_candle is True:
        signal = market.generate_trade_signal ()
        market.consume_trade_signal (signal)
        if (sims.simulator_on):
            sims.market_simulator_run (market)
        stats.stats_update_order_bulk(market)            
    
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
            if v == None:
                print ("Atleast one exchange need to be configured")
                return False
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
        elif k == 'stop_loss':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    tradingConfig ['stop_loss_enabled'] = ex_v
                elif ex_k == 'smart':
                    tradingConfig ['stop_loss_smart_rate'] = ex_v
                elif ex_k == 'rate':
                    tradingConfig ['stop_loss_rate'] = ex_v                    
        elif k == 'take_profit':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    tradingConfig ['take_profit_enabled'] = ex_v
                elif ex_k == 'rate':
                    tradingConfig ['take_profit_rate'] = ex_v                                    
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
        elif k == 'genetic_optimizer':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    if ex_v == True:
                        log.debug ("genetic_optimizer on")
                        sims.genetic_optimizer_on = True
                    else:
                        log.debug ("genetic_optimizer_on disabled")
                        sims.genetic_optimizer_on = False
                elif ex_k == 'config':
                    sims.gaDecisionConfig ['model_config'] = {"strategy": ex_v["strategy"]} 
                    sims.gaDecisionConfig ['model_type'] = 'simple'
                    for t_k, t_v in ex_v.get("trading", {}).iteritems():
                        if t_k == 'stop_loss':
                            for ex_tk, ex_tv in t_v.iteritems():
                                if ex_tk == 'enabled':
                                    sims.gaTradingConfig ['stop_loss_enabled'] = ex_tv
                                elif ex_tk == 'smart':
                                    sims.gaTradingConfig ['stop_loss_smart_rate'] = ex_tv
                                elif ex_tk == 'rate':
                                    sims.gaTradingConfig ['stop_loss_rate'] = ex_v                    
                        elif t_k == 'take_profit':
                            for ex_tk, ex_tv in t_v.iteritems():
                                if ex_tk == 'enabled':
                                    sims.gaTradingConfig ['take_profit_enabled'] = ex_tv
                                elif ex_tk == 'rate':
                                    sims.gaTradingConfig ['take_profit_rate'] = ex_tv                       
                elif ex_k == 'N_POP':
                    sims.ga_config["GA_NPOP"] = ex_v
                elif ex_k == 'N_GEN':
                    sims.ga_config["GA_NGEN"] = ex_v
                elif ex_k == 'N_MP':
                    sims.ga_config["GA_NMP"] = ex_v                                        
                
#     print ("v: %s"%str(tradingConfig))
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
    parser.add_argument("--ga_restart", help='restart genetic analysis from previous state', action='store_true')
    
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
        
    if (args.ga_restart):              
        log.debug ("ga_restart enabled")       
        sims.ga_restart = True
    else:
        log.debug ("import_only disabled")       
        sims.ga_restart = False           
        
    if (args.backtesting):              
        log.debug ("backtesting enabled")       
        sims.backtesting_on = True
        sims.simulator_on = True
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
        if sims.genetic_optimizer_on:
            print ("starting genetic backtesting optimizer")
            sims.ga_sim_main (OldMonkConfig, sims.gaDecisionConfig, sims.gaTradingConfig)
            print ("finished running genetic backtesting optimizer")
            sys.exit()
        OldMonk_init(decisionConfig, tradingConfig)
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
    except Exception as e:
        print ("Unexpected error: %s exception: %s"%(sys.exc_info(), e.message))
        OldMonk_end()
        raise
    #'''Not supposed to reach here'''
    print("\nOldMonk end")
    

#EOF
