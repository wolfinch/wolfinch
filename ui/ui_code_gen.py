#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: integrated UI impl.
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
