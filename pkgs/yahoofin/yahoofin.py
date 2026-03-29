#! /usr/bin/env python3
# '''
#  Wolfinch Auto trading Bot
#  Desc: Yahoofin exchange interactions for Wolfinch
#
#  Copyright: (c) 2017-2022 Wolfinch Inc.
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
try:
    from .yahoofin_websocket import WebsocketClient
except ImportError:
    from yahoofin_websocket import WebsocketClient
# import logging

from utils import getLogger

parser = args = None
log = getLogger ('Yahoofin')
log.setLevel(log.WARNING)
# logging.getLogger("urllib3").setLevel(logging.DEBUG)


# Wiki APIs - 
# https://www.reddit.com/r/sheets/wiki/apis/finance
# http://ogres-crypt.com/SMF/Elements/
#

# YAHOOFIN CONFIG FILE
API_BASE="https://api.yahoofin.com/"

class Yahoofin:
    session = None

    ###########################################################################
    #                       Logging in and initializing                       #
    ###########################################################################

    def __init__(self):
        self.session = requests.sessions.Session()
#         self.session.proxies = getproxies()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",            
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "Priority": "u=0, i",

        }
        self.session.headers = self.headers
        self.crumb = None
        self.cookie = None
        self._init_crumb()
        log.info("initialized yahoofin")
    
    def _init_crumb(self):
        """
        Initialize crumb and cookie for Yahoo Finance API authentication
        """
        try:
            # First, get the cookie by visiting Yahoo Finance
            crumb_url = "https://finance.yahoo.com/quote/AAPL"
            self.session.headers.update(self.headers)
            response = self.session.get(crumb_url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                log.warning("Failed to get initial cookie from Yahoo Finance. response: %d"% (response.status_code))
                return
            
            # log.debug("session cookies: %s" % self.session.cookies.get_dict())
            # log.debug("response headers: %s" % response.headers)
            # log.debug("session headers: %s" % self.session.headers)
            # Extract crumb from the page content
            import re
            crumb_pattern = r'"CrumbStore":\{"crumb":"([^"]+)"\}'
            match = re.search(crumb_pattern, response.text)
            
            # match = False
            if match:
                self.crumb = match.group(1)
                log.info(f"Successfully obtained crumb: {self.crumb[:10]}...")
            else:
                # Alternative method: try the crumb endpoint
                self._get_crumb_from_endpoint()
                
        except Exception as e:
            log.error(f"Error initializing crumb: {e}")
            self.crumb = None
    
    def _get_crumb_from_endpoint(self):
        """
        Alternative method to get crumb from Yahoo's crumb endpoint
        """
        try:
            # crumb_url = "https://query1.finance.yahoo.com/v1/test/getcrumb"
            crumb_url = "https://query2.finance.yahoo.com/v1/test/getcrumb"
            response = self.session.get(crumb_url, timeout=15)
            
            if response.status_code == 200:
                self.crumb = response.text.strip()
                log.info(f"Got crumb from endpoint: {self.crumb[:10]}...")
            else:
                log.warning("Failed to get crumb from endpoint. Response: %d response: %s" % (response.status_code, response.text))
                self.crumb = None
                exit(1)  # Exit if crumb cannot be obtained
        except Exception as e:
            log.error(f"Error getting crumb from endpoint: {e}")
    
    def _refresh_crumb(self):
        """
        Refresh the crumb when it expires
        """
        log.info("Refreshing crumb...")
        self._init_crumb()
    def get_url(self, url, use_crumb=True):
        """
            Flat wrapper for fetching URL directly
        """
        # Add crumb to URL if available and requested
        if use_crumb and self.crumb:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}crumb={self.crumb}"
        
        try:
            # log.debug("Fetching URL: %s" % url)
            resp = self.session.get(url, timeout=15)
            # log.debug("resp: %s"%(pprint.pformat(resp)))
            
            # Handle different status codes
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401 or resp.status_code == 429:
                # Unauthorized - crumb might be expired
                log.warning("Received 401, refreshing crumb...")
                self._refresh_crumb()
                # Retry once with new crumb
                if use_crumb and self.crumb:
                    separator = "&" if "?" in url.split("crumb=")[0] else "?"
                    url = f"{url.split('crumb=')[0].rstrip('&?')}{separator}crumb={self.crumb}"
                resp = self.session.get(url, timeout=15)
                return resp.json() if resp.status_code == 200 else {"error": f"Unable to fetch data from {url}, status code: {resp.status_code}"}
            else:
                return {"error": f"Unable to fetch data from {url}, status code: {resp.status_code}"}
                
        except Exception as e:
            log.error(f"Error fetching URL {url}: {e}")
            return {"error": f"Request failed: {str(e)}"}   
    ######## public function #########
    def get_financial_data (self, symbol, modules="price"):
        ### https://query2.finance.yahoo.com/v10/finance/quoteSummary/PTON?modules=defaultkeyStatistics,assetProfile,topHoldings,fundPerformance,fundProfile,financialData
        # modules :
        # assetProfile
        # balanceSheetHistory
        # balanceSheetHistoryQuarterly
        # calendarEvents
        # cashflowStatementHistory
        # cashflowStatementHistoryQuarterly
        # defaultKeyStatistics
        # earnings
        # earningsHistory
        # earningsTrend
        # esgScores
        # financialData - key-stats
        # fundOwnership
        # incomeStatementHistory
        # incomeStatementHistoryQuarterly
        # indexTrend
        # industryTrend
        # insiderHolders
        # insiderTransactions
        # institutionOwnership
        # majorDirectHolders
        # majorHoldersBreakdown
        # netSharePurchaseActivity
        # price
        # recommendationTrend
        # secFilings
        # sectorTrend
        # summaryDetail
        # summaryProfile
        # upgradeDowngradeHistory
        # pageviews
        # quotetype
        # all modules - 
        # https://query1.finance.yahoo.com/v10/finance/quoteSummary/FB?modules=assetProfile%2CbalanceSheetHistory%2CbalanceSheetHistoryQuarterly%2CcalendarEvents%2CcashflowStatementHistory%2CcashflowStatementHistoryQuarterly%2CdefaultKeyStatistics%2Cearnings%2CearningsHistory%2CearningsTrend%2CesgScores%2CfinancialData%2CfundOwnership%2CincomeStatementHistory%2CincomeStatementHistoryQuarterly%2CindexTrend%2CindustryTrend%2CinsiderHolders%2CinsiderTransactions%2CinstitutionOwnership%2CmajorDirectHolders%2CmajorHoldersBreakdown%2CnetSharePurchaseActivity%2Cprice%2CrecommendationTrend%2CsecFilings%2CsectorTrend%2CsummaryDetail%2CsummaryProfile%2CupgradeDowngradeHistory%2Cpageviews%2Cquotetype&ssl=true
        url = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/%s?\
modules=%s"%(symbol, modules)
        log.debug("get financial data for - %s url: %s"%(symbol, url))
        resp = self.get_url(url)
        log.debug("resp: %s"%(pprint.pformat(resp)))
        if resp.get('error'):
            log.critical ("error while fetch fin data for %s - error: %s"%(symbol, resp['error']))
            return None, resp['error']
        elif resp.get('quoteSummary') and resp['quoteSummary']["error"] != None:
            log.critical ("error while fetch fin data for %s - error: %s"%(symbol, resp['quoteSummary']["error"]))
            return None, resp['quoteSummary']["error"]
        return resp['quoteSummary']['result'][0], None
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
        resp = self.get_url(url, use_crumb=True)  # Quotes usually don't need crumb
        if resp.get('quoteResponse') and resp['quoteResponse']["error"] != None:
            log.critical ("error while get quotes - %s"%(resp['quoteResponse']["error"]))
            return None, resp['quoteResponse']["error"]
        elif resp.get('error'):
            return None, resp['error']
        return resp['quoteResponse']['result'], None        
    def get_options(self, sym, date=None):
        #https://query1.finance.yahoo.com/v7/finance/options/PTRA?date=1653004800
        log.debug ("date %s"%(date))
        date_opt="?date="+str(date) if date != None else ""
        api_url = "https://query1.finance.yahoo.com/v7/finance/options/%s%s"%(sym, date_opt)
        resp = self.get_url(api_url)
        if (resp.get("finance") and resp.get("finance").get("error")) or (resp.get('optionChain') and resp.get("optionChain").get("error")):
            log.critical ("error while get options - %s"%(resp))
            return None, "error while getting options"
        return resp['optionChain']['result'][0], None
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
    def subscribe_feed(self, products):
        self.ws_client.subscribe(products)
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
    print ("printing current crumbs - quotes %s"%(yf.crumb))
    resp, err = yf.get_quotes(symbol_list)
    if err == None:
        print ("quotes: \n %s"%(pprint.pformat(resp)))
    else:
        print("unable to find quotes, err %s"%err)
def print_fs(symbol):
    print ("printing current quotes")    
    resp, err = yf.get_financial_data(symbol)
    if err == None:
        print ("fs: \n %s"%(pprint.pformat(resp)))
    else:
        print("unable to find fs, err %s"%err)
def print_options(symbol, date=None):
    print ("printing current quotes")    
    resp, err = yf.get_options(symbol, date)
    if err == None:
        print ("options: \n %s"%(pprint.pformat(resp)))
    else:
        print("unable to find options, err %s"%err)        
def arg_parse():    
    global args, parser, YAHOOFIN_CONF
    parser = argparse.ArgumentParser(description='Yahoofin implementation')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument("--config", help='config file', required=False)
    parser.add_argument("--s", help='symbol', required=False)
    parser.add_argument("--ch", help='dump historic candles', required=False, action='store_true')
    parser.add_argument("--q", help='dump quotes', required=False, action='store_true')
    parser.add_argument("--fs", help='dump financial summary', required=False, action='store_true')
    parser.add_argument("--opt", help='dump options', required=False, action='store_true')
    args = parser.parse_args()
    if args.config:
        log.info ("using config file - %s"%(args.config))
        YAHOOFIN_CONF = args.config
######### ******** MAIN ****** #########
yf = None
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
    elif args.fs:
        yf = Yahoofin ()
        print_fs(args.s)
    elif args.opt:
        yf = Yahoofin ()
        print_options(args.s)        
    else:
        parser.print_help()
        exit(1)                            
#     sleep(10)
    print ("Done")
# EOF    
