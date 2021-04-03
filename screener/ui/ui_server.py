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
from flask import Flask
import threading
import logging
import screener

FORMAT = "[%(asctime)s %(levelname)s:%(name)s - %(funcName)20s(%(lineno)d) ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger("UI")
log.setLevel(logging.ERROR)

static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/')

UI_CODES_FILE = "data/ui_codes.json"
UI_TRADE_SECRET = None
UI_PAGE_SECRET = None

def server_main (port=8080):
        
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

    @app.route('/wolfinch/screener')
    @app.route('/<secret>/wolfinch/screener')
    def root_page_api(secret=None):
        if secret != get_ui_secret():
            log.error ("wrong code: " + str(secret))
            return ""
        return app.send_static_file('index.html')
        
    @app.route('/screener/api/data')
    def get_screener_data_api():     
        try:         
            log.debug("get data")
            screener_data = screener.get_screener_data()
            return json.dumps(screener_data)
        except Exception as e:
            log.error ("Unable to get screener data. Exception: %s", e)
            return "[]"
            
    log.debug("static_dir: %s root: %s" % (static_file_dir, app.root_path))
    
    log.debug ("starting server..")
    app.run(host='0.0.0.0', port=port, debug=False)
    log.error ("server finished!")

    
def ui_main (port=8080):
    try:
        log.info ("init UI server")
        server_main(port=port)
    except Exception as e:
        log.critical("ui excpetion e: %s" % (e))
        
def ui_init(port=8080):
    threading.Thread(target=ui_main, args=(port,)).start()
        
def arg_parse ():
    parser = argparse.ArgumentParser(description='Wolfinch screener UI Server')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--clean", help='Clean states and exit. Clear all the existing states', action='store_true')
    
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
