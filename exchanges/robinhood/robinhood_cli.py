#! /usr/bin/env python3
# '''
#  Wolfinch Auto trading Bot
#  Desc: Robinhood exchange interactions for Wolfinch
#
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
# '''
import pprint
from datetime import datetime, timedelta
from time import sleep
import time
from dateutil.tz import tzlocal, tzutc

from utils import getLogger, readConf
from market import  OHLC, feed_enQ, get_market_by_product, Order
from exchanges.robinhood import Robinhood
import logging

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("Robinhood").setLevel(logging.WARNING)

# ROBINHOOD CONFIG FILE
ROBINHOOD_CONF = 'config/robinhood.yml'


######## Functions for Main exec flow ########
def print_order_history(symbol, from_date, to_date):
    print ("printing order history")    
    orders = rbh.get_order_history(symbol, from_date, to_date)
    if len(orders):
        num_sell = num_buy = amt_sell = amt_buy = 0
        print ("retrieved %d orders: %s"%(len(orders), pprint.pformat(orders, 4)))
        print ("{:<6}{:^6}{:^6}{:^10}{:^10}{:^15}{:^15}".format("Ticker", "Side", "Size", "Price", "Type", "Status", "Date"))
        for o in orders:
            side        = o["side"]
            quant       = float(0 if o["quantity"]==None else o["quantity"])
            avg_price   = float(0 if o["average_price"]==None else o["average_price"])
            typ         = o["type"]
            status      = o["state"]
            if status == "filled":
                if side == "sell":
                    num_sell += quant
                    amt_sell += quant*avg_price
                else:
                    num_buy += quant
                    amt_buy += quant*avg_price                            
            print ("{:<6}{:^6}{:^6.0f}{:^10.3f}{:^10}{:^15}{:^15}".format(o["symbol"], side,
                         quant, avg_price, typ, status, o["created_at"]))
        #get curr quote
        quote = rbh.get_quote(symbol)        
        curr_price = float(quote["last_trade_price"])
        num_open = (num_buy-num_sell)
        cur_val = num_open*curr_price
        cur_bal = (amt_sell-amt_buy)
        total_profit = cur_bal + cur_val
        print("""Summary:
         num_buy: %d
         amt_buy: %.2f
         num_sell: %d
         amt_sell: %.2f
         num_open: %.2f(@%.2f)    curr_val: %.2f
         cur_bal: %.2f
         total_profit: %.2f"""%(
            num_buy, amt_buy, num_sell, amt_sell, num_open, curr_price, cur_val, cur_bal, total_profit))
    else:
        print("unable to find order history")
def print_options_order_history(symbol, from_date, to_date):
    print ("printing options order history")    
    orders = rbh.get_options_order_history(symbol, from_date, to_date)
    if len(orders):
        num_sell = num_buy = amt_sell = amt_buy = 0
        print ("retrieved %d orders"%(len(orders)))
        print ("{:<6}{:^6}{:^8}{:^8}{:^10}{:^10}{:^10}{:^10}{:^25}{:^10}{:^10}{:^15}{:^15}".format(
            "Ticker", "Side", "Action", "Size", "Price", "Type", "Status","dir", "strat", "type", "strike", "expiry", "Date"))
        for o in orders:
            sym         = o["chain_symbol"]
            side        = "NONE"# o["side"]
            status      = o["state"]            
            proc_quant       = float(0 if o["processed_quantity"]==None else o["processed_quantity"])
            quant       = float(0 if o["quantity"]==None else o["quantity"])
            if status == "cancelled" or status == "rejected":
                continue
            if o["closing_strategy"]:
                strat = o["closing_strategy"]
            else:
                strat = o["opening_strategy"]            
            if proc_quant != quant :# or strat == "long_call_spread":
                log.critical("ERROR!!! proc_quant != quant:: FIXME:: %s"%(pprint.pformat(o, 4)))
                raise
            avg_price   = float(0 if o["premium"]==None else o["premium"])
            typ         = o["type"]
            dir         = o["direction"]
            for leg in o["legs"]:
                exec_l = leg["executions"]
#                 if len(exec_l) > 1:
#                     log.critical ("FIXME: TODO: multi leg multi option o: %s"%(pprint.pformat(o, 4)))
#                     raise
                price = 0
                quant = 0
                for e in exec_l:
                    price_p = float(e["price"])*100
                    quant_p = float(e["quantity"])
                    price += price_p*quant_p
                    quant += quant_p
                side        = leg["side"]
                pos_effect  = leg["position_effect"]
                expiry_date = leg["option_det"]["expiration_date"]
                strike = leg["option_det"]["strike_price"]
                opt_type = leg["option_det"]["type"]                
                if status == "filled":
                    if side == "sell":
                        num_sell += quant
                        amt_sell += price
                    else:
                        num_buy += quant
                        amt_buy += price                
                print ("{:<6}{:^6}{:^8}{:^8.0f}{:^10.3f}{:^10}{:^10}{:^10}{:^25}{:^10}{:^10}{:^15}{:^15}".format(sym, side, pos_effect,
                         quant, price, typ, status, dir, strat, opt_type, strike, expiry_date, o["created_at"]))
        print("Summary:\n num_buy: %d \n amt_buy: %.2f \n num_sell: %d \n amt_sell: %.2f\n profit: %.2f"%(
            num_buy, amt_buy, num_sell, amt_sell, (amt_sell-amt_buy)))
    else:
        print("unable to find order history")
def print_current_options_positions(sym):
    print ("printing current option positions")    
    options_l = rbh.get_option_positions(sym)
    if len(options_l):
        print ("retrieved %d orders"%(len(options_l)))
        print ("{:<6}{:^8}{:^10}{:^10}{:^10}{:^10}{:^15}{:^10}{:^15}".format(
            "Ticker", "Size", "Price", "Type", "opt_type", "strike", "expiry", "Status", "Date"))
        for pos in options_l:
            sym     = pos["chain_symbol"]
            quant   = float(pos["quantity"])
            price   = float(pos["average_price"])
            type    = pos["type"]            
            opt_type    = pos["option_det"]["type"]
            status    = pos["option_det"]["state"]
            expiry_date    = pos["option_det"]["expiration_date"]            
            strike    = pos["option_det"]["strike_price"]                       
            print ("{:<6}{:^8.0f}{:^10.3f}{:^10}{:^10}{:^10}{:^15}{:^10}{:^15}".format(sym,
                         quant, price, type, opt_type, strike, expiry_date, status, pos["created_at"]))
def print_market_hrs():
    is_open, hrs = rbh.get_market_hrs()
    print ("%s"%(pprint.pformat(hrs, 4)))
def print_market_quote (sym):
    if sym==None or sym == "":
        print ("invalid symbol")
        return
    sym = sym.upper()    
    quote = rbh.get_quote(sym)
    print ("quote: %s"%(quote))
def exec_market_order(sym, action):
    if sym==None or sym == "":
        print ("invalid symbol")
        return
    print ("exec order action (%s) on symbol(%s)"%(action, sym))
    tr = TradeRequest(sym, action, 1, 0, 'market', 0, 0, 0) 
    if action == "buy":
        order = rbh.buy(tr)
    else:
        order = rbh.sell(tr)
    print ("order: %s"%(order))
def print_historic_candles(symbol, from_date=None, to_date=None):
    print ("printing order history")    
    candles = rbh.get_historic_rates(symbol, from_date, to_date)
    if candles != None:
        print ("candle history: \n len - %d"%(len(candles)))
    else:
        print("unable to find order history")    
def arg_parse():    
    global args, parser, ROBINHOOD_CONF
    parser = argparse.ArgumentParser(description='Robinhood Exch implementation')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--config", help='config file', required=False)
    parser.add_argument("--s", help='symbol', required=False)
    parser.add_argument("--oh", help='dump order history', required=False, action='store_true')
    parser.add_argument("--ooh", help='dump options order history', required=False, action='store_true')
    parser.add_argument("--ch", help='dump historic candles', required=False, action='store_true')    
    parser.add_argument("--cp", help='dump current positions', required=False, action='store_true')    
    parser.add_argument("--cop", help='dump current options positions', required=False, action='store_true')    
    parser.add_argument("--profit", help='total profit loss', required=False, action='store_true')
    parser.add_argument("--start", help='from date', required=False, action='store_true')          
    parser.add_argument("--end", help='to date', required=False, action='store_true')
    parser.add_argument("--hrs", help='market hourse', required=False, action='store_true')
    parser.add_argument("--quote", help='print quote', required=False, action='store_true')
    parser.add_argument("--buy", help='buy asset', required=False, action='store_true')
    parser.add_argument("--sell", help='sell asset', required=False, action='store_true')
    
    args = parser.parse_args()
    if args.config:
        log.info ("using config file - %s"%(args.config))
        ROBINHOOD_CONF = args.config
######### ******** MAIN ****** #########
if __name__ == '__main__':
    import argparse
    from market import TradeRequest
    
    parser = args = None

    print ("Robinhood exch CLI:")
    arg_parse()
    config = {"config": ROBINHOOD_CONF,
              "products" : [{"NIO":{}}, {"AAPL":{}}],
              "candle_interval" : 300,
              'backfill': {
                  'enabled'  : True,
                  'period'   : 5,  # in Days
                  'interval' : 300,  # 300s == 5m  
                }
              }
    
    
#     m = bnc.market_init('BTC-USD')

    # test historic rates
#     bnc.get_historic_rates('XLMUSDT')
#     
    # test buy order
#     tr = TradeRequest("XLMUSDT", 'BUY', 200, 200, "market", 100, 90)
#     order = bnc.buy(tr)
#     print ("buy order: %s" % (order))
#       
#     order = bnc.get_order("XLMUSDT", order.id)
#     print ("get buy order: %s" % (order))
#       
#     # test sell order
#     tr = TradeRequest("XLMUSDT", 'SELL', 200, 200, "market", 100, 90)
#     order = bnc.sell(tr)
#     print ("sell order: %s" % (order))        
#      
#     order = bnc.get_order("XLMUSDT", order.id)
#     print ("get sell order: %s" % (order))    
    
    if args.ch:
        rbh = Robinhood (config, stream=False)
        print_historic_candles(args.s, args.start, args.end)    
    elif args.oh:
        rbh = Robinhood (config, stream=False)
        print_order_history(args.s, args.start, args.end)
    elif args.ooh:
        rbh = Robinhood (config, stream=False)
        print_options_order_history(args.s, args.start, args.end)
    elif args.cp:
        rbh = Robinhood (config, stream=False)
        print_current_positions(args.s)
    elif args.cop:
        rbh = Robinhood (config, stream=False)
        print_current_options_positions(args.s)
    elif args.hrs:
        rbh = Robinhood (config, stream=False)
        print_market_hrs()
    elif args.quote:
        if args.s == None or args.s == "":
            print ("invalid symbol")
        else:    
            rbh = Robinhood (config, stream=False)
            print_market_quote(args.s)
    elif args.buy:
        rbh = Robinhood (config, stream=False)
        exec_market_order(args.s, "buy")
    elif args.sell:
        rbh = Robinhood (config, stream=False)
        exec_market_order(args.s, "sell")    
    else:
        parser.print_help()
        exit(1)                            
#     sleep(10)
    rbh.close()
#     print ("Done")
# EOF    
