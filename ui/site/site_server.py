#! /usr/bin/env python3
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
from flask import Flask, request, send_from_directory

from utils import getLogger

g_markets_list = None
g_active_market = {}  # {"CBPRO": "BTC-USD"}

log = getLogger ('UI')
log.setLevel(log.DEBUG)


def server_main (port=8080):
            
    app = Flask(__name__, static_folder='web/', static_url_path='/web/')
   
    @app.route('/js/<path:path>')
    def send_js_api(path):
        return send_from_directory('js', path)

    @app.route('/img/<filename>')
    def send_img(filename):
        return app.send_static_file('img/'+filename)
    
    @app.route('/stylesheet.css')
    def stylesheet_page_api():
        return app.send_static_file('stylesheet.css')

    @app.route('/')
    def root_page_api():
        return app.send_static_file('index.html')
            
    log.debug("root: %s" % ( app.root_path))
    
    log.debug ("starting server..")
    app.run(host='0.0.0.0', port=port, debug=False)
    log.error ("server finished!")    
    
def arg_parse ():
    parser = argparse.ArgumentParser(description='Wolfinch Auto Trading Bot UI Server')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--clean", help='Clean states and exit. Clear all the existing states', action='store_true')
    
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
