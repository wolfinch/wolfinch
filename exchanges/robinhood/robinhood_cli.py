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
# logging.getLogger("Robinhood").setLevel(logging.DEBUG)

# ROBINHOOD CONFIG FILE
ROBINHOOD_CONF = 'config/robinhood.yml'


######## Functions for Main exec flow ########
def get_option_chains(symbol, from_date, to_date, opt_type, sort="oi"):
    def key_func(k):
        #sort based on what?
        q = k["quote"]
        if sort == "oi":
            v = float(q["open_interest"] or 0)
        elif sort == "vol":
            v = float(q["volume"] or 0)
        elif sort == "iv":
            v = float(q["implied_volatility"] or 0)
        elif sort == "delta":
            v = float(q["delta"] or 0)
        elif sort == "theta":
            v = float(q["theta"] or 0)
        elif sort == "vega":
            v = float(q["vega"] or 0)
        elif sort == "best":
            #do better algo  for finding best option
            a = float(q["ask_price"] or 0)
            b = float(q["bid_price"] or 0) 
            if a == 0 or b == 0:
                v = 99999
            else:  
                v =  a - b
        return v
    
    #get chain_id
    instr = rbh.get_instrument_from_symbol(symbol)
    chain_id = instr["tradable_chain_id"]
    #get chain_summary, exp_dates
    opt_chains = rbh.get_option_chains_summary(chain_id)
    exp_list_l = opt_chains["expiration_dates"]
    #filter exp_list based on given time interval
    exp_list = []
    for exp in exp_list_l:
        exp_d = datetime.strptime(exp, "%Y-%m-%d")
        if from_date and from_date > exp_d:
            continue
        if to_date and to_date < exp_d:
            continue
        exp_list.append(exp)
    opt_c_d = {}
    #get chain @expiry
    for exp in exp_list:
        chain_l = rbh.get_option_chain(chain_id, exp, opt_type)
        #get option/instrument quote/details
        instr_list = []
        chain_d = {}
        for ch_e in chain_l:
            instr_list.append(ch_e["url"])
            chain_d[ch_e["url"]] = ch_e
        opt_data_l = rbh.get_option_marketdata(instr_list)
        #associate quote with instr
#         print("opt_data_l: %s"%(pprint.pformat(opt_data_l, 4)))        
        for opt_q in opt_data_l:
            if opt_q == None:
                continue
            chain_d[opt_q['instrument']]["quote"] = opt_q
        opt_c_l = []
        for opt_c in chain_d.values():
            #some of the entries may not have quote. remove those            
            if opt_c.get("quote"):
                opt_c_l.append(opt_c)
        opt_c_l.sort(reverse= (False if sort == "best" else True), key=key_func)
        opt_c_d [exp] = opt_c_l
    return opt_c_d
def print_option_chains(symbol, from_date, to_date, opt_type, best_num=0):
    global rbh
    #see if we have to sort, default "OI"
    sort = "oi"
    sort_opt = ["best", "oi", "vol", "iv", "delta", "theta", "vega"]
    if args.sort:
        if args.sort not in sort_opt:
            print ("Invalid sort method (%s) available options are - %s"%(args.sort, sort_opt))
            exit(1)
        sort = args.sort
    #get rbh instance
    rbh = Robinhood (config, stream=False, auth=True)
    #get option chains
    quote = rbh.get_quote(symbol)
    opt_c_d = get_option_chains(symbol, from_date, to_date, opt_type, sort=sort)
#     print ("quote: %s"%(pprint.pformat(opt_c_d, 4)))
    print ("{:<50} \n {:<50} ".format(" (%s) option chains for %s@%s"%(opt_type, symbol.upper(), quote["last_trade_price"]), 50*"-"))
    print ("{:<10}{:^10}{:<12}{:<12}{:^6}{:^6}{:^10}{:^10}{:^10}{:^10}".format("Strike", "Price", "Bid(#)", "Ask(#)", "OI", "Vol", "IV", "Delta", "Theta", "Vega"))
    for exp, opt_l in opt_c_d.items():
        print("{:>100}: {:<15} ".format("Exp", exp))
        num = 0
        for opt in opt_l:
            #print only the given num
            if best_num > 0 and best_num < num:
                break
            num += 1
            q = opt["quote"]
#             print ("quote: %s"%(pprint.pformat(opt, 4)))
            mp = float(q["mark_price"] or 0)
            bid_p = float(q["bid_price"] or 0) 
            bid_s = q["bid_size"]
            ask_p = float(q["ask_price"] or 0) 
            ask_s = q["ask_size"]            
            oi = q["open_interest"]
            vol = q["volume"]
            iv  = float(q["implied_volatility"] or 0)
            delta = float(q["delta"] or 0)
            theta = float(q["theta"] or 0)
            vega = float(q["vega"] or 0)
#             if oi > 0:
            print ("{:<10.2f}{:^10.2f}{:<12}{:<12}{:^6d}{:^6d}{:^10.4f}{:^10.4f}{:^10.4f}{:^10.4f}".format(float(opt["strike_price"]),
                         mp, "%.2f(%d)"%(bid_p,bid_s), "%.2f(%d)"%(ask_p,ask_s), oi, vol,  iv, delta,  theta, vega))
    
    
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
        print ("{:<6}{:^10}{:^15}{:^10}{:^6}{:^8}{:^8}{:^10}{:^10}{:^10}{:^10}{:^25}{:^15}".format(
            "Ticker", "strike", "expiry", "type", "Side", "Action", "Size", "Price", "Type", "Status","dir", "strat",  "Date"))
        for o in orders:
            sym         = o["chain_symbol"]
            side        = "NONE"# o["side"]
            status      = o["state"]            
            proc_quant       = float(0 if o["processed_quantity"]==None else o["processed_quantity"])
            req_quant       = float(0 if o["quantity"]==None else o["quantity"])
            if status == "rejected":
                continue
            if o["closing_strategy"]:
                strat = o["closing_strategy"]
            else:
                strat = o["opening_strategy"]
            #filter with strategy
            if args.filter != None and args.filter not in strat:
                continue
            #Partial execution..
#             if proc_quant != req_quant :# or strat == "long_call_spread":
#                 print("ERROR!!! proc_quant != quant:: FIXME:: %s"%(pprint.pformat(o, 4)))
#                 raise
            avg_price   = float(0 if o["premium"]==None else o["premium"])
            typ         = o["type"]
            dir         = o["direction"]
            for leg in o["legs"]:
                exec_l = leg["executions"]
                if len(exec_l) == 0:
                    #cancelled orders will have 0 eexecc, partially exec orders can be cancelled but non-zero exec
                    break
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
                if status != "rejected": #accommodate partial exec (filled, cancelled)
                    if side == "sell":
                        num_sell += quant
                        amt_sell += price
                    else:
                        num_buy += quant
                        amt_buy += price                
                print ("{:<6}{:^10}{:^15}{:^10}{:^6}{:^8}{:^8.0f}{:^10.3f}{:^10}{:^10}{:^10}{:^25}{:^15}".format(sym, 
                        strike, expiry_date, opt_type, side, pos_effect,
                         quant, price/quant, typ, status, dir, strat,  o["created_at"]))
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
    parser.add_argument("--n", help='number of..', required=False)    
    parser.add_argument("--oh", help='dump order history', required=False, action='store_true')
    parser.add_argument("--ooh", help='dump options order history', required=False, action='store_true')
    parser.add_argument("--oc", help='option chain details', required=False, action='store_true')
    parser.add_argument("--type", help='option type (put/call)', required=False)        
    parser.add_argument("--ch", help='dump historic candles', required=False, action='store_true')    
    parser.add_argument("--cp", help='dump current positions', required=False, action='store_true')    
    parser.add_argument("--cop", help='dump current options positions', required=False, action='store_true')    
    parser.add_argument("--profit", help='total profit loss', required=False, action='store_true')
    parser.add_argument("--start", help='from date (mm-dd-yyyy)', required=False)          
    parser.add_argument("--end", help='to date (mm-dd-yyyy)', required=False)
    parser.add_argument("--hrs", help='market hourse', required=False, action='store_true')
    parser.add_argument("--quote", help='print quote', required=False, action='store_true')
    parser.add_argument("--buy", help='buy asset', required=False, action='store_true')
    parser.add_argument("--sell", help='sell asset', required=False, action='store_true')
    parser.add_argument("--sort", help='sort', required=False)
    parser.add_argument("--filter", help='filter kind', required=False)
    
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

    start_t = end_t = None
    if args.start:
        start_t = datetime.strptime(args.start, "%m-%d-%Y")
    if args.end:
        end_t = datetime.strptime(args.end, "%m-%d-%Y")
    num = 0
    if args.n:
        num = int(args.n)
    if args.ch:
        rbh = Robinhood (config, stream=False)
        print_historic_candles(args.s, start_t, end_t)    
    elif args.oh:
        rbh = Robinhood (config, stream=False)
        print_order_history(args.s, start_t, end_t)
    elif args.ooh:
        rbh = Robinhood (config, stream=False)
        print_options_order_history(args.s, start_t, end_t)
    elif args.cp:
        rbh = Robinhood (config, stream=False)
        print_current_positions(args.s)
    elif args.oc:
        if args.type != "put" and args.type != "call":
            print ("invalid option type: %s"%(args.type))
            exit(1)
        print_option_chains(args.s,  start_t, end_t, args.type, num)        
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
