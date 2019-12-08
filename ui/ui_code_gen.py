#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: integrated UI impl.
#  Copyright: (c) 2017-2019 Joshith Rayaroth Koderi
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


import time
import json
import argparse
    
UI_CODES_FILE = "data/ui_codes.json"

ui_code = "1234"
trading_code = "1234"

def arg_parse ():
    global ui_code, trading_code
    parser = argparse.ArgumentParser(description='Wolfinch Auto Trading Bot UI Server Code Generator')

    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--web", help='web ui secret')
    parser.add_argument("--trading", help='trading secret')

    args = parser.parse_args()
    
    if args.web:
        ui_code = str(args.web)
    else:
        # Simple code is no code. TODO: FIXME: FIXME: 
        ui_code =  int(time.time()/(60*60*24))
        
    if args.trading:
        trading_code = str(args.trading)
    else:
        # Simple code is no code. TODO: FIXME: FIXME: 
        trading_code =  int(time.time()/(60*60*24))
        
                
######### ******** MAIN ****** #########
if __name__ == '__main__':
    
    arg_parse ()
    
    ui_code_o = {'TRADE_SECRET': str(trading_code), 'UI_SECRET': str(ui_code)}
    
    print("\nui_code: %s trade_code: %s"%(ui_code, trading_code))    
    with open (UI_CODES_FILE, 'w') as fp:
        json.dump(ui_code_o, fp)
        
    print ("UI CODES GENERATED!!")
#EOF
