#! /usr/bin/env python

'''
 SkateBot Auto trading Bot
 Desc: Generate manual trading signal
 (c) Joshith Rayaroth Koderi
'''

import json
import argparse
import os
import pprint

parser = argparse.ArgumentParser(description='Generate manual trading signal')
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                    help='an integer for the accumulator')

parser.add_argument('--exchange',  help='Exchange', required=True)
parser.add_argument('--product',  help='Product', required=True)
parser.add_argument('--size',  help='BUY in $USD | SELL BTC', required=True)
parser.add_argument('--limit', help='generate sell request', required=True, type=float)
parser.add_argument('type', choices =['BUY', 'SELL'], help='generate sell request')

args = parser.parse_args()

'''
        -- Manual Override file: "override/TRADE_<exchange_name>.<product>"
            Json format:
            {
             product : <ETH-USD|BTC-USD>
             type    : <BUY|SELL>
             size    : <$USD|BTC>
             price   : <limit-price>
            }
'''

print (str(args))
json_data = {}

json_data['product'] = args.product
json_data['price'] = args.limit

amount = 0.0
if (args.type == 'BUY' ):
    json_data["type"] = 'BUY'
    #see if the size is in USD
    if (args.size[-1] != '$'):
        print ("ERROR: Please Specify Buy size in USD. (eg. 2000$)")
        exit()
    size = float (args.size[:-1])
    size = round(float(size)/args.limit, 8)
    json_data['size'] = size
else:
    json_data["type"] = 'SELL'
    json_data['size'] = float(args.size)

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

#end