#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Main UI impl
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
import sys
from decimal import getcontext
import argparse
import os
import json
import time
from flask import Flask, request, send_from_directory

from utils import getLogger
import db_events

# TODO: FIXME, remove static
# g_markets_list = {"CBPRO":["BTC-USD", "ETH-USD"], "BNC":["BTC-INR", "ETH-INR"]}
g_markets_list = None
g_active_market = {}  # {"CBPRO": "BTC-USD"}

UI_TRADE_SECRET = "3254"

log = getLogger ('UI')
log.setLevel(log.INFO)
# EXCH_NAME = "CBPRO"
# PRODUCT_ID = "BTC-USD"

static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/')
# POSITION_STATS_FILE = "stats_positions_%s_%s.json"%("CBPRO", "BTC-USD")
MARKET_STATS = "stats_market_%s_%s.json"


# TRADED_STATS_FILE = "stats_traded_orders_%s_%s.json"%("CBPRO", "BTC-USD")
def server_main (port=8080, mp_pipe=None):
    
#     # init db_events
#     if not db_events.init(EXCH_NAME, PRODUCT_ID):
#         log.error ("db_events init failure")
#         return
    
    app = Flask(__name__, static_folder='web/', static_url_path='/web/')

    def get_ui_secret():
        return str(int(time.time() / (60 * 60 * 24)))
    
    @app.route('/js/<path:path>')
    def send_js_api(path):
        return send_from_directory('js', path)

    @app.route('/<secret>/oldmonk/stylesheet.css')
    def stylesheet_page_api(secret):
        if secret != get_ui_secret():
            log.error ("wrong code: " + secret)
            return ""
        return app.send_static_file('stylesheet.css')

    @app.route('/<secret>/oldmonk/chart.html')
    def chart_page_api(secret):
        if secret != get_ui_secret():
            log.error ("wrong code: " + secret)
            return ""
        return app.send_static_file('chart.html')

    @app.route('/<secret>/oldmonk/trading.html')
    def trading_page_api(secret):
        if secret != get_ui_secret():
            log.error ("wrong code: " + secret)
            return ""
        return app.send_static_file('trading.html')    

    @app.route('/<secret>/oldmonk')
    def root_page_api(secret):
        if secret != get_ui_secret():
            log.error ("wrong code: " + secret)
            return ""
        return app.send_static_file('index.html')        

    @app.route('/api/get_markets')
    def get_markets_api():
        global g_markets_list
        try:
            if not g_markets_list:
                msg = {"type": "GET_MARKETS"}
                if mp_pipe:
                    msg = mp_send_recv_msg (mp_pipe, msg, True)
                    if msg:
                        msg_type = msg.get("type")
                        if msg_type == "GET_MARKETS_RESP":
                            log.debug ("GET_MARKETS_RESP recv")
                            g_markets_list = msg.get("data")
                            if not g_markets_list:
                                err = "invalid market list payload"
                                log.error (err)
                                raise Exception (err)                            
                        else:
                            err = "invalid ui resp msg type: %s" % msg_type
                            log.error (err)
                            raise Exception (err)
                else:
                    err = "server connection can't be found!"
                    log.error (err)
                    raise Exception (err)
            data = {"all": g_markets_list}
            if g_active_market.get("EXCH_NAME") and  g_active_market.get("PRODUCT_ID"):
                data["active"] = {g_active_market["EXCH_NAME"] : g_active_market["PRODUCT_ID"]}
            return json.dumps(data)
        except Exception as e:
            log.error ("Unable to get market list. Exception: %s", e)
            return "{}"

    @app.route('/api/set_active_market', methods=["POST"])
    def set_active_market_api():
        global g_active_market
        try:
            data = request.form.to_dict()
            if len(data.keys()) > 0 :
                exch_name = data.keys()[0]
                prod_id = data.values()[0].encode('ascii')
                g_active_market = {"EXCH_NAME": exch_name, "PRODUCT_ID": prod_id}
                log.info ("set active market: %s " % (g_active_market))
                # init db_events
                if not db_events.init(exch_name, prod_id):
                    log.error ("db_events init failure")
                else:
                    log.info ("init markets success")
            return "{}"
        except Exception as e:
            log.error ("Unable to set active market. Exception: %s", e)
            return "{}"

    @app.route('/api/market_stats')
    def market_stats_api():
        try:
            if len(g_active_market.keys()) <= 0:
                log.error ("active market not set")
                return "{}"
            m_stats_file = MARKET_STATS % (g_active_market["EXCH_NAME"], g_active_market["PRODUCT_ID"])
            with open (os.path.join(static_file_dir, m_stats_file), 'r') as fp:
                s = fp.read()
                if not len (s):
                    return "{}"
                else:
                    return s
        except Exception:
            return "{}"
            
    @app.route('/api/candles')
    def candle_list_api():
        if len(g_active_market.keys()) <= 0:
            log.error ("active market not set")
            return "[]"        
        period = request.args.get('period', default=1, type=int)
        return db_events.get_all_candles(period)
        
    @app.route('/api/positions')
    def position_list_api():
        if len(g_active_market.keys()) <= 0:
            log.error ("active market not set")
            return "[]"        
        return db_events.get_all_positions()
            
    @app.route('/api/manual_order', methods=["POST"])
    def exec_manual_order_api():

        def ret_code(err):
            return json.dumps(err)       
                
        data = request.form.to_dict()
        if len(data.keys()) <= 0 :
            err = "error: invalid request data"
            log.error (err)
            return ret_code(err)      
        
        cmd = data.get('cmd', "buy")
        req_number = int(data.get('req_number', 0))
        req_code = str(data.get('req_code', ""))
        exch_name = str(data.get('exch_name', ""))
        prod_id = str(data.get('product', ""))
                
        log.info ("manual order: type: %s req_number: %d req_code: %s exch: %s prod: %s" % (
            cmd, req_number, req_code, exch_name, prod_id))
        
        if (exch_name == "" or prod_id == "" or req_code == "" or req_number <= 0):
            err = "error: incorrect request data"
            log.error (err)
            return ret_code(err)
        
        if req_code != UI_TRADE_SECRET:
            err = "incorrect secret"
            log.error (err)
            return ret_code(err)
        
        err = "success"
        if abs(req_number) > 3 or req_number == 0:
            err = "error: invalid req_number: %s" % (str(req_number))
            log.error (err)
            return ret_code(err)
        
        signal = 0
        if cmd == "sell":
            signal = -req_number
        elif cmd == "buy":
            signal = req_number
        else:
            err = "error: invalid cmd: %s" % (cmd)
            log.error (err)
            return ret_code(err)
        
        msg = {"type": "TRADE", "exchange": exch_name, "product": prod_id, "side": cmd, "signal": signal}
        if mp_pipe:
            mp_send_recv_msg(mp_pipe, msg)
        else:
            err = "server connection can't be found!"
            log.error (err)
        return ret_code(err)      
            
    log.debug("static_dir: %s root: %s" % (static_file_dir, app.root_path))
    
    log.debug ("starting server..")
    app.run(host='0.0.0.0', port=port, debug=False)
    log.error ("server finished!")

        
def mp_send_recv_msg(mp_pipe, msg, wait_resp=False):
    try:
        mp_pipe.send(msg)
        if False == wait_resp:
            return
        # wait for 10 secs for resp
        while mp_pipe.poll(10):
            msg = mp_pipe.recv()
            err = msg.get("error", None)
            if  err != None:
                log.error ("error in the pipe, ui finished: msg:%s" % (err))
                raise Exception("UI error - %s" % (err))
            else:
                return msg
        return None
    except Exception as e:
        log.critical ("exception %s on ui" % (e))
        raise e

    
def ui_main (port=8080, mp_conn_pipe=None):
    try:
        server_main(port=port, mp_pipe=mp_conn_pipe)
    except Exception as e:
        log.critical("ui excpetion e: %s" % (e))
        mp_send_recv_msg(mp_conn_pipe, {"error": "exception: %s" % (e)})
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
    
    getcontext().prec = 8  # decimal precision
    
    print("Starting OldMonk UI server..")
    
    try:
        log.debug ("Starting Main forever loop")
        server_main ()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    except:
        print ("Unexpected error: ", sys.exc_info())
        raise
    # '''Not supposed to reach here'''
    print("\nOldMonk UI Server end")

# EOF
