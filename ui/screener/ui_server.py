#! /usr/bin/env python3
#
# Wolfinch Auto trading Bot
# Desc: Screener UI impl
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


import sys
from decimal import getcontext
import argparse
import os
import json
from threading import Lock
from flask import Flask, request, send_from_directory

from utils import getLogger
# from . import db_events

# g_markets_list = None
# g_active_market = {}  # {"CBPRO": "BTC-USD"}


log = getLogger ('UI')
log.setLevel(log.DEBUG)


static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/')
# MARKET_STATS = "stats_market_%s_%s.json"

UI_CODES_FILE = "data/ui_codes.json"
UI_TRADE_SECRET = None
UI_PAGE_SECRET = None

g_mp_lock = None

def server_main (port=8080, mp_pipe=None):
    
#     # init db_events
#     if not db_events.init(EXCH_NAME, PRODUCT_ID):
#         log.error ("db_events init failure")
#         return
    
    global g_mp_lock
    g_mp_lock = Lock()
        
    app = Flask(__name__, static_folder='web/', static_url_path='/web/')
    
    def get_ui_secret():
        return str(UI_PAGE_SECRET) if UI_PAGE_SECRET != None else None
        
    @app.route('/wolfinch/screener/js/<path>')    
    @app.route('/<secret>/wolfinch/screener/js/<path>')
    def send_js_api(path, secret=None):
        return app.send_static_file('js/'+path)

    @app.route('/wolfinch/screener/stylesheet.css')
    @app.route('/<secret>/wolfinch/screener/stylesheet.css')
    def stylesheet_page_api(secret=None):
        if secret != get_ui_secret():
            log.error ("wrong code: " + str(secret))
            return ""
        return app.send_static_file('stylesheet.css')
#     
#     @app.route('/wolfinch/screener/chart.html')
#     @app.route('/<secret>/wolfinch/screener/chart.html')
#     def chart_page_api(secret=None):
#         if secret != get_ui_secret():
#             log.error ("wrong code: " + str(secret))
#             return ""
#         return app.send_static_file('chart.html')
# 
#     @app.route('/wolfinch/screener/trading.html')
#     @app.route('/<secret>/wolfinch/screener/trading.html')
#     def trading_page_api(secret=None):
#         if secret != get_ui_secret():
#             log.error ("wrong code: " + str(secret))
#             return ""
#         return app.send_static_file('trading.html')

    @app.route('/wolfinch/screener')
    @app.route('/<secret>/wolfinch/screener')
    def root_page_api(secret=None):
        if secret != get_ui_secret():
            log.error ("wrong code: " + str(secret))
            return ""
        return app.send_static_file('index.html')

#     @app.route('/api/market_stats')
#     def market_stats_api():
#         try:
#             if len(g_active_market) <= 0:
#                 log.error ("active market not set")
#                 return "{}"
#             m_stats_file = MARKET_STATS % (g_active_market["EXCH_NAME"], g_active_market["PRODUCT_ID"])
#             with open (os.path.join(static_file_dir, m_stats_file), 'r') as fp:
#                 s = fp.read()
#                 if not len (s):
#                     return "{}"
#                 else:
#                     return s
#         except Exception:
#             return "{}"   
        
    @app.route('/api/screener/data')
    def get_screener_data_api():     
#         from_time = request.args.get('from_time', default=0, type=int)
#         to_time = request.args.get('to_time', default=0, type=int)        
#         exch_name = str(request.args.get('exch_name', ""))
#         prod_id = str(request.args.get('product', ""))
        
#         return db_events.get_all_candles(period)
        try:
#             if exch_name == "" or prod_id == "":
#                 log.error ("invalid markets")
#                 return "[]"
            
            msg = {"type": "GET_SCREENER_DATA",
#                    "from_time": from_time,
#                    "to_time": to_time,                   
#                    "exchange": exch_name,
#                    "product": prod_id
                   }
#             dataSet = [
#          {"symbol": "aapl", "last_price": "10.2", "change": "10", "pct_change": "2"},
#          {"symbol": "codx", "last_price": "13.2", "change": "20", "pct_change": "20"}            
#              ]            
            log.debug("get data")
            screener_data = []
            if mp_pipe:
                msg = mp_send_recv_msg (mp_pipe, msg, True)
                if msg:
                    msg_type = msg.get("type")
                    if msg_type == "GET_SCREENER_DATA_RESP":
                        log.debug ("GET_SCREENER_DATA_RESP recv")
                        screener_data = msg.get("data")
                        if not screener_data:
                            err = "invalid screener_data payload"
                            log.error (err)
                            raise Exception (err)
                        else:
                            log.info ("screener_data - %s"%(screener_data))
                    else:
                        err = "invalid ui resp msg type: %s" % msg_type
                        log.error (err)
                        raise Exception (err)
            else:
                err = "server connection can't be found!"
                log.error (err)
                raise Exception (err)
            return json.dumps(screener_data)
        except Exception as e:
            log.error ("Unable to get screener data. Exception: %s", e)
            return "[]" #json.dumps(dataSet) #"[]" 
            
#     @app.route('/api/positions')
#     def position_list_api():
#         if len(g_active_market) <= 0:
#             log.error ("active market not set")
#             return "[]"        
#         return db_events.get_all_positions()
            
#     @app.route('/api/manual_order', methods=["POST"])
#     def exec_manual_order_api():
# 
#         def ret_code(err):
#             return json.dumps(err)       
#                 
#         data = request.form.to_dict()
#         if len(data) <= 0 :
#             err = "error: invalid request data"
#             log.error (err)
#             return ret_code(err)      
#         
#         cmd = data.get('cmd', "buy")
#         req_number = int(data.get('req_number', 0))
#         req_code = str(data.get('req_code', ""))
#         exch_name = str(data.get('exch_name', ""))
#         prod_id = str(data.get('product', ""))
#                 
#         log.info ("manual order: type: %s req_number: %d req_code: %s exch: %s prod: %s" % (
#             cmd, req_number, req_code, exch_name, prod_id))
#         
#         if (exch_name == "" or prod_id == "" or req_code == "" or req_number <= 0):
#             err = "error: incorrect request data"
#             log.error (err)
#             return ret_code(err)
#         
#         if req_code != UI_TRADE_SECRET:
#             err = "incorrect secret"
#             log.error (err)
#             return ret_code(err)
#         
#         err = "success"
#         if abs(req_number) > 3 or req_number == 0:
#             err = "error: invalid req_number: %s" % (str(req_number))
#             log.error (err)
#             return ret_code(err)
#         
#         signal = 0
#         if cmd == "sell":
#             signal = -req_number
#         elif cmd == "buy":
#             signal = req_number
#         else:
#             err = "error: invalid cmd: %s" % (cmd)
#             log.error (err)
#             return ret_code(err)
#         
#         msg = {"type": "TRADE", "exchange": exch_name, "product": prod_id, "side": cmd, "signal": signal}
#         if mp_pipe:
#             mp_send_recv_msg(mp_pipe, msg)
#         else:
#             err = "server connection can't be found!"
#             log.error (err)
#         return ret_code(err)      
            
    log.debug("static_dir: %s root: %s" % (static_file_dir, app.root_path))
    
    log.debug ("starting server..")
    app.run(host='0.0.0.0', port=port, debug=False)
    log.error ("server finished!")

        
def mp_send_recv_msg(mp_pipe, msg, wait_resp=False):
    global g_mp_lock
    try:
        g_mp_lock.acquire()
        #there seems to be a weird timing issue causing msg flips
        #drain everything in the pipe before we start
        while mp_pipe.poll(0):
            msg = mp_pipe.recv()
            log.error("recv unknown msg(%s) recvd (draining)"%(msg.get("type")))
        mp_pipe.send(msg)
        if False == wait_resp:
            g_mp_lock.release()
            return
        # wait for 10 secs for resp
        while mp_pipe.poll(10):
            log.debug("recv success")            
            msg = mp_pipe.recv()
            err = msg.get("error", None)
            if  err != None:
                log.error ("error in the pipe, ui finished: msg:%s" % (err))
                raise Exception("UI error - %s" % (err))
            else:
                g_mp_lock.release()
                return msg
        g_mp_lock.release()
        log.error("recv failed")                    
        return None
    except Exception as e:
        log.critical ("exception %s on ui" % (e))
        g_mp_lock.release()        
        raise e

    
def ui_main (port=8080, mp_conn_pipe=None):
    try:
        log.info ("init UI server")
        server_main(port=port, mp_pipe=mp_conn_pipe)
    except Exception as e:
        log.critical("ui excpetion e: %s" % (e))
        mp_send_recv_msg(mp_conn_pipe, {"error": "exception: %s" % (e)})
        mp_conn_pipe.close()

        
def arg_parse ():
    parser = argparse.ArgumentParser(description='Wolfinch screener UI Server')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--clean", help='Clean states and exit. Clear all the existing states', action='store_true')
#     parser.add_argument("--config", help='Wolfinch Global config file')
#     parser.add_argument("--backtesting", help='do backtesting', action='store_true')
    
    args = parser.parse_args()
    
    if (args.clean):
        exit (0)


######### ******** MAIN ****** #########
if __name__ == '__main__':
    
    arg_parse()
    
    getcontext().prec = 8  # decimal precision
    
    print("Starting Wolfinch screener UI server..")
    
    try:
        log.debug ("Starting screener UI forever loop")
        server_main ()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    except:
        print ("Unexpected error: ", sys.exc_info())
        raise
    # '''Not supposed to reach here'''
    print("\nWolfinch screener UI Server end")

# EOF
