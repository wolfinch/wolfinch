#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: Main UI impl
#  Copyright: (c) 2017-2020 Joshith Rayaroth Koderi
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
from . import db_events

g_markets_list = None
g_active_market = {}  # {"CBPRO": "BTC-USD"}


log = getLogger ('UI')
log.setLevel(log.INFO)


static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/')
MARKET_STATS = "stats_market_%s_%s.json"

UI_CODES_FILE = "data/ui_codes.json"
UI_TRADE_SECRET = "1234"
UI_PAGE_SECRET = "1234"

g_mp_lock = None

def load_ui_codes ():
    global UI_TRADE_SECRET, UI_PAGE_SECRET
    log.info ("loading ui codes")
    try:
        with open (UI_CODES_FILE, 'r') as fp:
            codes = json.load(fp)            
            UI_TRADE_SECRET, UI_PAGE_SECRET = codes['TRADE_SECRET'], codes['UI_SECRET']
    except Exception as e:
        log.critical ("exception %s on ui while reading UI codes" % (e))        
        raise e    
        

def server_main (port=8080, mp_pipe=None):
    
#     # init db_events
#     if not db_events.init(EXCH_NAME, PRODUCT_ID):
#         log.error ("db_events init failure")
#         return
    
    global g_mp_lock
    g_mp_lock = Lock()
    
    load_ui_codes ()
    
    app = Flask(__name__, static_folder='web/', static_url_path='/web/')

    def get_ui_secret():
        return str(UI_PAGE_SECRET)
    
    @app.route('/<secret>/wolfinch/js/<path>')
    def send_js_api(secret, path):
        return app.send_static_file('js/'+path)

    @app.route('/<secret>/wolfinch/stylesheet.css')
    def stylesheet_page_api(secret):
        if secret != get_ui_secret():
            log.error ("wrong code: " + secret)
            return ""
        return app.send_static_file('stylesheet.css')

    @app.route('/<secret>/wolfinch/chart.html')
    def chart_page_api(secret):
        if secret != get_ui_secret():
            log.error ("wrong code: " + secret)
            return ""
        return app.send_static_file('chart.html')

    @app.route('/<secret>/wolfinch/trading.html')
    def trading_page_api(secret):
        if secret != get_ui_secret():
            log.error ("wrong code: " + secret)
            return ""
        return app.send_static_file('trading.html')    

    @app.route('/<secret>/wolfinch')
    def root_page_api(secret):
        if secret != get_ui_secret():
            log.error ("wrong code: " + secret)
            return ""
        return app.send_static_file('index.html')        

    @app.route('/api/get_markets')
    def get_markets_api():
        global g_markets_list, g_active_market
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
            if not( g_active_market.get("EXCH_NAME") and  g_active_market.get("PRODUCT_ID")):
                #set the first one in the list as default active
                if (len(g_markets_list)):
                    exch_name  = list(g_markets_list.keys())[0]
                if (len(g_markets_list[exch_name])):
                    market = g_markets_list[exch_name][0]
                
                if exch_name and market:
                    g_active_market = {"EXCH_NAME": exch_name, "PRODUCT_ID": market['product_id'],
                            "BUY_PAUSED": market["buy_paused"], "SELL_PAUSED": market["sell_paused"]}
            if g_active_market.get("EXCH_NAME") and  g_active_market.get("PRODUCT_ID"): 
                data["active"] = {"EXCH_NAME": g_active_market["EXCH_NAME"],
                                  "PRODUCT_ID": g_active_market["PRODUCT_ID"],
                                  "BUY_PAUSED": g_active_market["BUY_PAUSED"],
                                  "SELL_PAUSED": g_active_market["SELL_PAUSED"]}

            return json.dumps(data)
        except Exception as e:
            log.error ("Unable to get market list. Exception: %s", e)
            return "{}"

    @app.route('/api/set_active_market', methods=["POST"])
    def set_active_market_api():
        global g_active_market
        try:
            data = request.form.to_dict()
#             log.info ("data:%s"%(data))
            if len(data) > 0 :
                exch_name = str(list(data.keys())[0])
                prod_id = str(list(data.values())[0])

                log.info ("exch:%s prod_id:%s"%(exch_name, prod_id))
                
                for market in g_markets_list[exch_name]:
#                     log.info ("market :%s prod_id:%s"%(market, prod_id))
                    if market["product_id"] == prod_id:
                        g_active_market = {"EXCH_NAME": exch_name, "PRODUCT_ID": prod_id,
                                "BUY_PAUSED": market["buy_paused"], "SELL_PAUSED": market["sell_paused"]}
                        break                
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

    @app.route('/api/pause_market', methods=["POST"])
    def pause_market_api():

        def ret_code(err):
            return json.dumps(err)       
                
        data = request.form.to_dict()
        if len(data) <= 0 :
            err = "error: invalid request data"
            log.error (err)
            return ret_code(err)      
        
        log.info ("data: %s"%(data))
        buy_pause = bool(int(data.get('buy_pause', False)))
        sell_pause = bool(int(data.get('sell_pause', False)))        
        req_code = str(data.get('req_code', ""))
        exch_name = str(data.get('exch_name', ""))
        prod_id = str(data.get('product', ""))
                
        log.info ("buy_pause (%d) sell_pause (%d) exch: %s prod: %s" % (buy_pause, sell_pause, exch_name, prod_id))
        
        if (exch_name == "" or prod_id == "" or req_code == ""):
            err = "error: incorrect request data"
            log.error (err)
            return ret_code(err)
        
        if req_code != UI_TRADE_SECRET:
            err = "incorrect secret"
            log.error (err)
            return ret_code(err)
        
        err = "success"
        
        msg = {"type": "PAUSE_TRADING", "exchange": exch_name, "product": prod_id, "buy_pause": buy_pause, "sell_pause": sell_pause}
        if mp_pipe:
            log.info ("sending buy_pause (%d) sell_pause(%d) msg to tranding engine"%(buy_pause, sell_pause))
            mp_send_recv_msg(mp_pipe, msg)
            g_active_market["BUY_PAUSED"] = buy_pause
            g_active_market["SELL_PAUSED"] = sell_pause            
            for market in g_markets_list[exch_name]:
                if market["product_id"] == prod_id:
                    market["buy_paused"] = buy_pause
                    market["sell_paused"] = sell_pause                    
                    break            
        else:
            err = "server connection can't be found!"
            log.error (err)
        return ret_code(err)            

    @app.route('/api/market_stats')
    def market_stats_api():
        try:
            if len(g_active_market) <= 0:
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
        period = request.args.get('period', default=1, type=int)
        start_time = request.args.get('start_time', default=0, type=int)
        exch_name = str(request.args.get('exch_name', ""))
        prod_id = str(request.args.get('product', ""))
        
        try:
            if exch_name == "" or prod_id == "":
                log.error ("invalid markets")
                return "[]"
                        
            msg = {"type": "GET_MARKET_INDICATORS",
                   "start_time": start_time,
                   "periods": period,
                   "exchange": exch_name,
                   "product": prod_id
                   }
            if mp_pipe:
                msg = mp_send_recv_msg (mp_pipe, msg, True)
                if msg:
                    msg_type = msg.get("type")
                    if msg_type == "GET_MARKET_INDICATORS_RESP":
                        log.debug ("GET_MARKET_INDICATORS_RESP recv")
                        candle_list = msg.get("data")
                        if not candle_list:
                            err = "invalid candle_list payload"
                            log.error (err)
                            raise Exception (err)
                        else:
                            log.info ("num candles - %d"%(len(candle_list)))
                    else:
                        err = "invalid ui resp msg type: %s" % msg_type
                        log.error (err)
                        raise Exception (err)
            else:
                err = "server connection can't be found!"
                log.error (err)
                raise Exception (err)
            def serialize (obj):
                if  hasattr(obj, "__dict__" ):
                    return obj.__dict__
                if hasattr(obj, "__slots__" ):
                    return obj.serialize()
            return json.dumps(candle_list, default=serialize)
        except Exception as e:
            log.error ("Unable to get candle list. Exception: %s", e)
            return "[]"        
        
    @app.route('/api/positions')
    def position_list_api():     
        from_time = request.args.get('from_time', default=0, type=int)
        to_time = request.args.get('to_time', default=0, type=int)        
        exch_name = str(request.args.get('exch_name', ""))
        prod_id = str(request.args.get('product', ""))
        
#         return db_events.get_all_candles(period)
        try:
            if exch_name == "" or prod_id == "":
                log.error ("invalid markets")
                return "[]"
            
            msg = {"type": "GET_MARKET_POSITIONS",
                   "from_time": from_time,
                   "to_time": to_time,                   
                   "exchange": exch_name,
                   "product": prod_id
                   }
            if mp_pipe:
                msg = mp_send_recv_msg (mp_pipe, msg, True)
                if msg:
                    msg_type = msg.get("type")
                    if msg_type == "GET_MARKET_POSITIONS_RESP":
                        log.debug ("GET_MARKET_POSITIONS_RESP recv")
                        pos_list = msg.get("data")
                        if not pos_list:
                            err = "invalid pos_list payload"
                            log.error (err)
                            raise Exception (err)
                        else:
                            log.info ("num pos - %d"%(len(pos_list)))
                    else:
                        err = "invalid ui resp msg type: %s" % msg_type
                        log.error (err)
                        raise Exception (err)
            else:
                err = "server connection can't be found!"
                log.error (err)
                raise Exception (err)
            return str(pos_list)
        except Exception as e:
            log.error ("Unable to get position list. Exception: %s", e)
            return "[]" 
            
#     @app.route('/api/positions')
#     def position_list_api():
#         if len(g_active_market) <= 0:
#             log.error ("active market not set")
#             return "[]"        
#         return db_events.get_all_positions()
            
    @app.route('/api/manual_order', methods=["POST"])
    def exec_manual_order_api():

        def ret_code(err):
            return json.dumps(err)       
                
        data = request.form.to_dict()
        if len(data) <= 0 :
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
            msg = mp_pipe.recv()
            err = msg.get("error", None)
            if  err != None:
                log.error ("error in the pipe, ui finished: msg:%s" % (err))
                raise Exception("UI error - %s" % (err))
            else:
                g_mp_lock.release()
                return msg
        g_mp_lock.release()        
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
    parser = argparse.ArgumentParser(description='Wolfinch Auto Trading Bot UI Server')

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
    
    print("Starting Wolfinch UI server..")
    
    try:
        log.debug ("Starting Main forever loop")
        server_main ()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    except:
        print ("Unexpected error: ", sys.exc_info())
        raise
    # '''Not supposed to reach here'''
    print("\nWolfinch UI Server end")

# EOF
