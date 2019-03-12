#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Generate manual trading signal
# Copyright 2018, Joshith Rayaroth Koderi. All Rights Reserved.
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

import json
import argparse
import os
import pprint
from decimal import *

getcontext().prec = 8 #decimal precision

######### ******** MAIN ****** #########
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate manual trading signal')
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                    help='an integer for the accumulator')
    
    parser.add_argument('--exchange',  help='Exchange', required=True)
    parser.add_argument('--product',  help='Product', required=True)
    parser.add_argument('--size',  help='BUY in $USD | SELL BTC', required=True)
    parser.add_argument('type', choices =['BUY', 'SELL'], help='generate sell request')
    parser.add_argument('--limit', help='limit price', required=True, type=float)
    parser.add_argument('--stop', help='Post the order at specified (STOP) price', type=float )
    
    args = parser.parse_args()
    
    '''
            -- Manual Override file: "override/TRADE_<exchange_name>.<product>"
                Json format:
                {
                 product : <ETH-USD|BTC-USD>
                 side    : <BUY|SELL>
                 size    : <$USD|BTC>
                 type    : <limit|market>
                 price   : <limit-price>
                 stop  : <Post order At Price>
                }
    '''
    
    print (str(args))
    json_data = {}
    
    json_data['product'] = args.product
    json_data['price'] = args.limit
    json_data['stop'] = args.stop
    amount = 0.0
    json_data['type'] = ('stop' if (args.stop) else 'limit')
    if (args.type == 'BUY' ):
        json_data["side"] = 'BUY'
        #see if the size is in USD
        if (args.size[-1] != '$'):
            print ("ERROR: Please Specify Buy size in USD. (eg. 2000$)")
            exit()
        size = Decimal (args.size[:-1])
        size = round(Decimal(size)/Decimal(args.limit), 8)
        json_data['size'] = size
        if (args.stop and args.limit > args.stop):
            print ("ERROR: 'stop' price has to be higher than 'limit' for BUY")
            exit()
    else:
        json_data["side"] = 'SELL'
        json_data['size'] = Decimal(args.size)
        if (args.stop and args.limit < args.stop):
            print ("ERROR: 'stop' price has to be lower than 'limit' for SELL")
            exit()    
    
    print ("Order Being generated on Exchange: %s \n*****************\n %s"
          "\n****************\n"%( args.exchange, pprint.pformat(json_data, 4, 10)))
    
    yes = {'yes','y', 'ye'}
    
    print ("\nConfirm Order (yes/no):")
    choice = raw_input().lower()
    if choice in yes:
        order_file_name = "override/TRADE_%s.%s"%(args.exchange, args.product)
        with open (order_file_name, "w") as fp:
            json.dump(json_data, fp)
        print ("Order Generated!")
    else:
        print ("Order Cancelled!\n")
    
#EOF