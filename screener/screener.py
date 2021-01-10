#! /usr/bin/env python3
'''
# Wolfinch Stock Screener
# Desc: Main File implements Screener Entry points
#  Copyright: (c) 2017-2021 Joshith Rayaroth Koderi
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
'''

import time
import sys
import os
import traceback
import argparse
from decimal import getcontext
import random
# import logging
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "../pkgs"))

from utils import getLogger, get_product_config, load_config, get_config
# import sims
# import exchanges
import db
# import stats
import ui
# from ui import ui_conn_pipe

import nasdaq
import yahoofin as yf

# mpl_logger = logging.getLogger('matplotlib')
# mpl_logger.setLevel(logging.WARNING)
log = getLogger('Screener')
log.setLevel(log.DEBUG)

ticker_import_time = 0
all_tickers = []
YF = None

# global Variables
MAIN_TICK_DELAY = 0.500  # 500 milli


def screener_init():
    global YF
    # seed random
    random.seed()

    # 1. Retrieve states back from Db
#     db.init_order_db(Order)
    register_screeners()
    
    YF = yf.Yahoofin ()

    # setup ui if required
    ui.integrated_ui = True
    ui.port = 8080
    if ui.integrated_ui:
        log.info("ui init")
        ui.ui_conn_pipe = ui.ui_mp_init(ui.port, ui.screener.ui_main)
        if ui.ui_conn_pipe is None:
            log.critical("unable to setup ui!! ")
            print("unable to setup UI!!")
            sys.exit(1)

def screener_end():
    log.info("Finalizing Screener")

    # stop stats thread
    log.info("waiting to stop stats thread")

    ui.ui_mp_end()
    log.info("all cleanup done.")


def screener_main():
    """
    Main Function for Screener
    """

    integrated_ui = ui.integrated_ui
    ui_conn_pipe = ui.ui_conn_pipe

    sleep_time = MAIN_TICK_DELAY
    while True:
        if integrated_ui == True:
            process_ui_msgs(ui_conn_pipe)        
        cur_time = time.time()
#         update_data()
        process_screeners()
        # '''Make sure each iteration take exactly LOOP_DELAY time'''
        sleep_time = (MAIN_TICK_DELAY -(time.time()- cur_time))
#         if sleep_time < 0 :
#             log.critical("******* TIMING SKEWED(%f)******"%(sleep_time))
        sleep_time = 0 if sleep_time < 0 else sleep_time
        time.sleep(sleep_time)
    # end While(true)

def register_screeners():
    log.debug("registering screeners")
    
def update_data():
    log.debug("updating data")
    get_all_tickers_info()
    
def process_screeners ():
    log.debug("processing screeners")
    
def get_all_tickers ():
    global ticker_import_time, all_tickers
    log.debug ("get all tickers")
    if ticker_import_time + 24*3600 < int(time.time()) :
        log.info ("renew tickers list")
        t_l = nasdaq.get_all_tickers_gt50m()
        if t_l:
            all_tickers = []
            for ticker in t_l:
                all_tickers.append(ticker["symbol"].strip())            
            ticker_import_time = int(time.time())        
    return all_tickers    
def get_all_tickers_info():
    BATCH_SIZE = 400
    sym_list = get_all_tickers()
    log.debug("num tickers(%d)"%(len(sym_list)))
    ticker_stats = []
    i = 0
    while i < len(sym_list):
        ts, err =  YF.get_quotes(sym_list[i: i+BATCH_SIZE])
        if err == None:
            ticker_stats += ts
            i += BATCH_SIZE
        else:
            time.sleep(2)    
    log.debug("(%d)ticker stats retrieved"%( len(ticker_stats)))
    
def process_ui_msgs(ui_conn_pipe):
    try:
        while ui_conn_pipe.poll():
            msg = ui_conn_pipe.recv()
            err = msg.get("error", None)
            if  err is not None:
                log.error("error in the pipe, ui finished: msg:%s" %(err))
                raise Exception("UI error - %s" %(err))
            else:
                log.info ("ui_msg: %s"%(msg))
                msg_type = msg.get("type")
                if msg_type == "GET_SCREENER_DATA":
                    process_get_screener_data(msg)
                else:
                    log.error("Unknown ui msg type: %s", msg_type)
    except Exception as e:
        log.critical("exception %s on ui" %(str(e)))
        raise e

def process_get_screener_data(msg):
    log.info("msg %s"%(msg))

    dataSet = [
         {"symbol": "aapl", "last_price": "10.2", "change": "10", "pct_change": "2"},
         {"symbol": "codx", "last_price": "13.2", "change": "20", "pct_change": "20"}            
             ] 
    
    msg["type"] = "GET_SCREENER_DATA_RESP"
    msg["data"] = dataSet #{}
    ui.ui_conn_pipe.send(msg)    

def clean_states():
    ''' 
    clean states
    '''
    log.info("Clearing Db")
    db.clear_db()

def arg_parse():
    '''
    arg parse
    '''
    parser = argparse.ArgumentParser(description='Wolfinch Screener')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0.1')
    parser.add_argument("--clean",
                        help='Clean states,dbs and exit. Clear all the existing states',
                        action='store_true')
    parser.add_argument("--config", help='Screener Global config file')
    parser.add_argument("--restart", help='restart from the previous state', action='store_true')

    args = parser.parse_args()

    if args.clean:
        clean_states()
        exit(0)

    if args.config:
        log.debug("config file: %s" % (str(args.config)))
        if False == load_config(args.config):
            log.critical("Config parse error!!")
            parser.print_help()
            exit(1)
        else:
            log.debug("config loaded successfully!")
#             exit(0)
    else:
        pass
#         parser.print_help()
#         exit(1)

    if args.restart:
        log.debug("restart enabled")
        print("Restarting from previous state")
    else:
        log.debug("restart disabled")

######### ******** MAIN ****** #########
if __name__ == '__main__':
    '''
    main entry point
    '''
    arg_parse()
    getcontext().prec = 8  # decimal precision
    print("Starting Wolfinch Screener..")
    try:
        screener_init()
        log.info("Starting Main forever loop")
        print("Starting Main forever loop")            
        screener_main()
    except(KeyboardInterrupt, SystemExit):
        screener_end()
        sys.exit()
    except Exception as e:
        log.critical("Unexpected error: exception: %s" %(traceback.format_exc()))
        print("Unexpected error: exception: %s" %(traceback.format_exc()))
        screener_end()
        raise
#         traceback.print_exc()
#         os.abort()
    # '''Not supposed to reach here'''
    print("\nScreener end")

# EOF
