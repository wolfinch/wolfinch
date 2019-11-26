#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Main File implements Bot
# Copyright 2017-2019, Joshith Rayaroth Koderi. All Rights Reserved.
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
import os
import traceback
import argparse
from decimal import getcontext
import random
import logging, matplotlib
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)

from utils import getLogger, get_product_config, load_config, get_config
import sims
import exchanges
from market import market_init, market_setup, get_market_list, feed_Q_process_msg, feed_deQ, get_market_by_product
import db
import stats
import ui

log = getLogger ('OldMonk')
log.setLevel(log.INFO)

gRestart = False

# global Variables
MAIN_TICK_DELAY = 0.500  # 500 milli


def OldMonk_init():
    
    # seed random
    random.seed()
        
    # 1. Retrieve states back from Db
#     db.init_order_db(Order)

    # setup ui if required
    if ui.integrated_ui:
        ui.ui_conn_pipe = ui.ui_mp_init(ui.port)
        if ui.ui_conn_pipe == None :
            log.critical ("unable to setup ui!! ")
            print ("unable to setup UI!!")
            sys.exit(1)
    
    # 2. Init Exchanges
    exchanges.init_exchanges(get_config())
    
    # 3. Init markets
    market_init (exchanges.exchange_list, get_product_config)
    
    # 4. Setup markets
    market_setup(restart=gRestart)
    
    # 5. start stats thread
    stats.start()

    
def OldMonk_end():
    log.info ("Finalizing OldMonk")
    exchanges.close_exchanges ()
    
    # stop stats thread
    log.info ("waiting to stop stats thread")
    stats.stop()
    
    ui.ui_mp_end()
    log.info ("all cleanup done.")
    

def oldmonk_main ():
    """
    Main Function for OldMonk
    """
    feed_deQ_fn = feed_deQ
    feed_Q_process_msg_fn = feed_Q_process_msg
    
    integrated_ui = ui.integrated_ui
    ui_conn_pipe = ui.ui_conn_pipe
    
    sleep_time = MAIN_TICK_DELAY
    while (True) : 
        cur_time = time.time()
#         log.critical("Current (%d) Sleep time left:%s"%(cur_time, str(sleep_time)))         
        # check for the msg in the feed Q and process, with timeout
        msg = feed_deQ_fn(sleep_time) 
#         log.critical("Current (%d)"%(time.time()))
        while (msg != None):
            feed_Q_process_msg_fn (msg)
            msg = feed_deQ_fn(0)
        if integrated_ui == True:
            process_ui_msgs (ui_conn_pipe)
        for market in get_market_list():
            process_market (market)
        # '''Make sure each iteration take exactly LOOP_DELAY time'''
        sleep_time = (MAIN_TICK_DELAY - (time.time() - cur_time))
#         if sleep_time < 0 :
#             log.critical ("******* TIMING SKEWED (%f) ******"%(sleep_time))
        sleep_time = 0 if (sleep_time < 0) else sleep_time     
    # end While(true)

    
def process_market (market):
#     """ 
#     processing routine for one exchange
#     """
    log.debug ("processing Market: exchange (%s) product: %s" % (market.exchange_name, market.name))
    # update various market states on tick
    market.update_market_states()
    
    # Trade only on primary markets
    if market.new_candle is True:
        if market.primary is True:
            signal = market.generate_trade_signal ()
            market.consume_trade_signal (signal)
            if (sims.simulator_on):
                sims.market_simulator_run (market)
        stats.stats_update_order_bulk(market)            
    
    # check pending trades periodically and takes actions (this logic is rate-limited)
    market.watch_pending_orders()
    
    # commit market states to the db periodically (this logic is rate-limited)
    market.lazy_commit_market_states()

    
def process_ui_trade_notif (msg):
    exch = msg.get("exchange")
    product = msg.get("product")
    side = msg.get("side")
    signal = msg.get("signal")
    m = get_market_by_product (exch, product)
    if not m:
        log.error ("Unknown exchange/product exch: %s prod: %s" % (exch, product))
    else:
        log.info ("Manual Trade Req: exch: %s prod: %s side: %s signal: %s" % (exch, product, side, str(signal)))
        m.consume_trade_signal(signal)

def process_ui_pause_trading_notif (msg):
    exch = msg.get("exchange")
    product = msg.get("product")
    buy_pause = msg.get("buy_pause")
    sell_pause = msg.get("sell_pause")
    
    m = get_market_by_product (exch, product)
    if not m:
        log.error ("Unknown exchange/product exch: %s prod: %s" % (exch, product))
    else:
        log.info ("pause trading on exch: %s prod: %s" % (exch, product))
        m.pause_trading(buy_pause, sell_pause)    
        
def process_ui_get_markets_rr (msg, ui_conn_pipe):
    log.debug ("enter")
    m_dict = {}
    for m in get_market_list():
        p_list = m_dict.get(m.exchange_name)
        if not p_list:
            m_dict[m.exchange_name] = [{"product_id": m.product_id,
                     "buy_paused": m.trading_paused_buy, "sell_paused": m.trading_paused_sell}]
        else:
            p_list.append({"product_id": m.product_id, 
                           "buy_paused": m.trading_paused_buy, "sell_paused": m.trading_paused_sell})
    
    msg ["type"] = "GET_MARKETS_RESP"
    msg ["data"] = m_dict
    ui_conn_pipe.send(msg)

    
def process_ui_msgs(ui_conn_pipe):
    try:
        while ui_conn_pipe.poll():
            msg = ui_conn_pipe.recv()
            err = msg.get("error", None)
            if  err != None:
                log.error ("error in the pipe, ui finished: msg:%s" % (err))
                raise Exception("UI error - %s" % (err))
            else:
                msg_type = msg.get("type")
                if msg_type == "TRADE":
                    process_ui_trade_notif (msg)
                elif msg_type == "GET_MARKETS":
                    process_ui_get_markets_rr (msg, ui_conn_pipe)
                elif msg_type == "PAUSE_TRADING":
                    process_ui_pause_trading_notif (msg)
                else:
                    log.error ("Unknown ui msg type: %s", msg_type)
    except Exception as e:
        log.critical ("exception %s on ui" % (e))
        raise e

    
def clean_states ():
    log.info ("Clearing Db")
    db.clear_db()
    stats.clear_stats()
        
def arg_parse ():
    global gRestart
    parser = argparse.ArgumentParser(description='OldMonk Auto Trading Bot')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--clean", help='Clean states,dbs and exit. Clear all the existing states', action='store_true')
    parser.add_argument("--config", help='OldMonk Global config file')
    parser.add_argument("--backtesting", help='do backtesting', action='store_true')
    parser.add_argument("--import_only", help='do import only', action='store_true')
    parser.add_argument("--restart", help='restart from the previous state', action='store_true')        
    parser.add_argument("--ga_restart", help='restart genetic analysis from previous state', action='store_true')
    
    args = parser.parse_args()
    
    if (args.clean):
        clean_states ()
        exit (0)
                 
    if (args.config):
        log.debug ("config file: %s" % args.config)
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
        
    if (args.import_only):              
        log.debug ("import_only enabled")       
        sims.import_only = True
        sims.genetic_optimizer_on = False        
        sims.backtesting_on = False
    else:
        log.debug ("import_only disabled")       
        sims.import_only = False          
        
    if (args.restart):              
        log.debug ("restart enabled")
        print ("Restarting from previous state")
        gRestart = True
    else:
        log.debug ("restart disabled")       
        gRestart = False  
                
    if (args.ga_restart):              
        log.debug ("ga_restart enabled")       
        sims.ga_restart = True
    else:
        log.debug ("import_only disabled")       
        sims.ga_restart = False           
        
    if (args.backtesting):
        log.debug ("backtesting enabled")       
        sims.backtesting_on = True
        # sims.simulator_on = True
#     else:
#         log.debug ("backtesting disabled")       
#         sims.backtesting_on = False        
    
#     log.debug("sims.backtesting_on: %d"%(sims.backtesting_on))
#     exit(1)

    
######### ******** MAIN ****** #########
if __name__ == '__main__':
    
    arg_parse()
    
    getcontext().prec = 8  # decimal precision
    
    print("Starting OldMonk..")
    
    try:
        if sims.genetic_optimizer_on:
            print ("starting genetic backtesting optimizer")
            sims.ga_sim_main (get_config(), get_product_config)
            print ("finished running genetic backtesting optimizer")
            sys.exit()
        OldMonk_init()
        if sims.import_only:
            log.info ("import only")
            raise SystemExit
        
        if (sims.backtesting_on):
            sims.market_backtesting_run (sims.simulator_on)
            if ui.integrated_ui:
                oldmonk_main()
            else:
                raise SystemExit
        else:
            log.debug ("Starting Main forever loop")
            oldmonk_main ()
    except (KeyboardInterrupt, SystemExit):
        OldMonk_end()
        sys.exit()
    except Exception as e:
        log.critical ("Unexpected error: %s exception: %s" % (sys.exc_info(), e.message))        
        print ("Unexpected error: %s exception: %s" % (sys.exc_info(), e.message))
        OldMonk_end()
        raise
#         traceback.print_exc()
#         os.abort()
    # '''Not supposed to reach here'''
    print("\nOldMonk end")

# EOF
