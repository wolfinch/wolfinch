#! /usr/bin/env python3
# '''
#  Wolfinch Auto trading Bot
#  Desc: Yahoofin exchange interactions for Wolfinch
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
import json
import pprint
from datetime import datetime, timedelta
from time import sleep
import time
from dateutil.tz import tzlocal, tzutc
import requests
from .yahoofin_websocket import WebsocketClient

from utils import getLogger

parser = args = None
log = getLogger ('Yahoofin')
log.setLevel(log.WARNING)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

# YAHOOFIN CONFIG FILE
API_BASE="https://api.yahoofin.com/"

class Yahoofin:
    session = None

    ###########################################################################
    #                       Logging in and initializing                       #
    ###########################################################################

    def __init__(self):
        self.session = requests.session()
#         self.session.proxies = getproxies()
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",  # noqa: E501
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Connection": "keep-alive",
        }
        self.session.headers = self.headers
        log.info("initialized yahoofin")
    def get_url(self, url):
        """
            Flat wrapper for fetching URL directly
        """
        return self.session.get(url, timeout=15).json()
    ######## public function #########
    def get_historic_candles (self, symbol=None, interval=None, start_time=None, end_time=None):
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?symbol=%s&period1=%d&period2=%d&interval=%s"%(#&includePrePost=true
            symbol, symbol, start_time, end_time, interval)
        log.debug("importing historic candles url - %s"%(url))        
        resp = self.get_url(url)
        if resp['chart']["error"] != None:
            log.critical ("error while importing candles - %s"%(resp['chart']["error"]))
            return None, resp['chart']["error"]
        return resp['chart']['result'][0], None
    def get_quotes(self, sym_list):
        log.debug ("sym_list %s"%(sym_list))
        if (len(sym_list) == 0):
            return None
        fields = "&fields=longName,shortName,regularMarketPrice,regularMarketChange,regularMarketChangePercent,marketCap,underlyingSymbol,underlyingExchangeSymbol,headSymbolAsString,regularMarketVolume,averageDailyVolume10Day,averageDailyVolume3Month,uuid,regularMarketOpen,fiftyTwoWeekLow,fiftyTwoWeekHigh"
        sym_str= ",".join(sym_list)
        url = "https://query1.finance.yahoo.com/v7/finance/quote?&symbols="+sym_str+fields
        resp = self.get_url(url)
        if resp['quoteResponse']["error"] != None:
            log.critical ("error while get quotes - %s"%(resp['quoteResponse']["error"]))
            return None, resp['quoteResponse']["error"]
        return resp['quoteResponse']['result'], None        

    def get_trending(self, num=5):
        api_url = "https://query1.finance.yahoo.com/v1/finance/trending/US?count="+num
        resp = self.get_url(api_url)
        if resp['finance']["error"] != None:
            log.critical ("error while get trending - %s"%(resp['finance']["error"]))
            return None, resp['finance']["error"]
        return resp['finance']['result'], None
    def get_market_time(self):
        api_url = "https://finance.yahoo.com/_finance_doubledown/api/resource/finance.market-time"
        resp = self.get_url(api_url)
        if resp.get('status') == None:
            log.critical ("error while get market time - %s"%(resp))
            return None, "unable to get market time"
        return resp, None        
            
    def start_feed(self, products, cb_fn):
#         products += ["LYFT", "ES=F", "YM=F", "NQ=F", "RTY=F", "CL=F", "GC=F", "SI=F", "EURUSD=X", "^TNX", "^VIX"]
        self.ws_client = WebsocketClient(products=products, feed_recv_hook=cb_fn)
        self.ws_client.start()
    def stop_feed(self):
        self.ws_client.close()

######## Functions for Main exec flow ########
def print_historic_candles(symbol, interval, from_date, to_date):
    print ("printing order history")    
    resp, err = yf.get_historic_candles(symbol, interval, from_date, to_date)
    if err == None:
        print ("candle history: \n %s"%(pprint.pformat(resp)))
    else:
        print("unable to find order history, err %s"%err)
def print_quotes(symbol_list):
    print ("printing current quotes")    
    resp, err = yf.get_quotes(symbol_list)
    if err == None:
        print ("quotes: \n %s"%(pprint.pformat(resp)))
    else:
        print("unable to find quotes, err %s"%err)

def arg_parse():    
    global args, parser, YAHOOFIN_CONF
    parser = argparse.ArgumentParser(description='Yahoofin implementation')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--config", help='config file', required=False)
    parser.add_argument("--s", help='symbol', required=False)
    parser.add_argument("--ch", help='dump historic candles', required=False, action='store_true')
    parser.add_argument("--q", help='dump quotes', required=False, action='store_true')
    args = parser.parse_args()
    if args.config:
        log.info ("using config file - %s"%(args.config))
        YAHOOFIN_CONF = args.config
######### ******** MAIN ****** #########
if __name__ == '__main__':
    import argparse
    
    print ("Testing Yahoofin exch:")
    arg_parse()
    if args.ch:
        yf = Yahoofin ()
        print_historic_candles(args.s, "60m", 1586873400, 1588660532)
    if args.q:
        yf = Yahoofin ()
        print_quotes(["TSLA", "codx"])        
    else:
        parser.print_help()
        exit(1)                            
#     sleep(10)
    print ("Done")
# EOF    
