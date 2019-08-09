#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Main File implements Bot
# Copyright 2018, OldMonk Bot. All Rights Reserved.
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
import os
from flask import request

from flask import Flask, request, send_from_directory

from utils import getLogger
from utils.readconf import readConf
from dateparser import conf

import db_events
log = getLogger ('UI')
log.setLevel(log.DEBUG)

static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/')
POSITION_STATS_FILE = "stats_positions_%s_%s.json"%("CBPRO", "BTC-USD")
MARKET_STATS = "stats_market_%s_%s.json"%("CBPRO", "BTC-USD")
TRADED_STATS_FILE = "stats_traded_orders_%s_%s.json"%("CBPRO", "BTC-USD")
def server_main (mp_pipe=None):
    
    # init db_events
    if not db_events.init():
        log.error ("db_events init failure")
        return
    
    app = Flask(__name__, static_folder='web/', static_url_path='/web/')

    @app.route('/js/<path:path>')
    def send_js(path):
        return send_from_directory('js', path)
    @app.route('/oldmonk/stylesheet.css')
    def stylesheet_page():
        return app.send_static_file('stylesheet.css')
    @app.route('/oldmonk/chart.html')
    def chart_page():
        return app.send_static_file('chart.html')
    @app.route('/oldmonk/trading.html')
    def trading_page():
        return app.send_static_file('trading.html')    
    @app.route('/oldmonk')
    def root_page():
        return app.send_static_file('index.html')        
    @app.route('/api/order_data')
    def trade_data():
        try:
            with open (os.path.join(static_file_dir, POSITION_STATS_FILE), 'r') as fp:
                s = fp.read()
                if not len (s):
                    return "{}"
                else:
                    return s
        except Exception:
            return "{}"        
    @app.route('/api/market_stats')
    def market_stats():
        try:
            with open (os.path.join(static_file_dir, MARKET_STATS), 'r') as fp:
                s = fp.read()
                if not len (s):
                    return "{}"
                else:
                    return s
        except Exception:
            return "{}"
            
    @app.route('/api/candles')
    def candle_list():
        period = request.args.get('period', default = 1, type = int)
        return db_events.get_all_candles(period)
        
    @app.route('/api/positions')
    def position_list():
        return db_events.get_all_positions()
    
    @app.route('/api/manual_order')
    def exec_manual_order():
        cmd = request.args.get('cmd', default = "buy", type = str)
        req_number = request.args.get('req_number', default = 0, type = int)
        req_code = request.args.get('req_code', default = "", type = str)
        
        log.info ("manual order: type: %s req_number: %d req_code: %s"%(cmd, req_number, req_code))
        
        #TODO: FIXME: do code validation
        
        err = "success"
        if abs(req_number) > 3 or req_number == 0:
            err = "error: invalid req_number: %s"%(str(req_number))
            log.error (err)
            return err
        
        signal = 0
        if cmd == "sell":
            signal = -req_number
        elif cmd == "buy":
            signal = req_number
        else:
            err = "error: invalid cmd: %s"%(cmd)
            log.error (err)
            return err
        
        msg = {"exchange": "CBPRO", "product": "BTC-USD", "side": cmd, "signal": signal}
        if mp_pipe:
            mp_pipe.send(msg)
        return err      
            
    log.debug("static_dir: %s root: %s"%(static_file_dir, app.root_path))
    
    log.debug ("starting server..")
    app.run(host='0.0.0.0', port=80, debug=False)
    log.error ("server finished!")
        
def ui_main (mp_conn_pipe):
    try:
        server_main(mp_conn_pipe)
    except Exception as e:
        log.critical("ui excpetion e: %s"%(e))
        mp_conn_pipe.send({"error": "exception: %s"%(e)})
        mp_conn_pipe.close()
        
def arg_parse ():
    parser = argparse.ArgumentParser(description='OldMonk Auto Trading Bot UI Server')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--clean", help='Clean states and exit. Clear all the existing states', action='store_true')
#     parser.add_argument("--config", help='OldMonk Global config file')
#     parser.add_argument("--backtesting", help='do backtesting', action='store_true')
    
    args = parser.parse_args()
    
    if (args.clean):
        exit (0)

######### ******** MAIN ****** #########
if __name__ == '__main__':
    
    arg_parse()
    
    getcontext().prec = 8 #decimal precision
    
    print("Starting OldMonk UI server..")
    
    try:
        log.debug ("Starting Main forever loop")
        server_main ()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    except:
        print ("Unexpected error: ",sys.exc_info())
        raise
    #'''Not supposed to reach here'''
    print("\nOldMonk UI Server end")
    

#EOF
