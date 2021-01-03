#! /usr/bin/env python3
'''
# Nasdaq Interface Implementation
# Desc: Implements various Nasdaq Interfaces
#  Copyright: (c) 2017-2021 Joshith Rayaroth Koderi
#  This file is part of Wolfinch Screener.
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
'''

import time
import sys
# import os
import traceback
# import argparse
import pprint
from decimal import getcontext
import random
import logging
from utils import getLogger #, get_product_config, load_config, get_config
# import sims
# import exchanges
# import db
import requests


# mpl_logger.setLevel(logging.WARNING)
log = getLogger('Screener')
log.setLevel(log.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

GET_ALL_TICKERS_API = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25000&offset=0"

Session = None
def get_url(url):
    global Session
    if Session == None:
        Session = requests.session()
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",  # noqa: E501
            "Connection": "keep-alive",
        }
        Session.headers = headers
        log.info("initialized nasdaq Session")
    log.debug ("get url: %s"%(url))
    return Session.get(url, timeout=15).json()    

def get_all_tickers ():
    log.debug ("get all tickers")
    data = get_url (GET_ALL_TICKERS_API)
    if data:
        all_tickers = data.get("data").get("table").get("rows")
        log.debug ("all tickers %s, total-number (%d)"%(pprint.pformat(all_tickers), len(all_tickers)))
        return all_tickers
    
def get_all_tickers_gt50m ():
    log.debug ("get all tickers")
    mcap = "&marketcap=mega|large|mid|small|micro"
    api = GET_ALL_TICKERS_API+mcap
    data = get_url (api)
    if data:
        all_tickers = data.get("data").get("table").get("rows")
        log.debug ("tickers > 50m mcap %s, total-number (%d)"%(pprint.pformat(all_tickers), len(all_tickers)))
        return all_tickers
        
def get_all_tickers_lt50m ():
    log.debug ("get all tickers")
    mcap = "&marketcap=nano"
    api = GET_ALL_TICKERS_API+mcap
    data = get_url (api)
    if data:
        all_tickers = data.get("data").get("table").get("rows")
        log.debug ("tickers < 50m mcap %s, total-number (%d)"%(pprint.pformat(all_tickers), len(all_tickers)))
        return all_tickers
    
def get_ticker_stats(ticker):
    GET_STATS_API = "https://api.nasdaq.com/api/quote/%s/info?assetclass=stocks"%(ticker)
    log.debug ("get ticker stats")
    data = get_url (GET_STATS_API)
    if data:
        log.debug ("ticker %s, total-number (%d)"%(pprint.pformat(data), len(data)))
        return data["data"]

def get_tickers_stats(tickers):
    GET_STATS_API = "https://api.nasdaq.com/api/quote/watchlist?"
    log.debug ("get ticker stats")
    if not len(tickers):
        log.error ("invalid symbol list")
        return None
    sym_list = ""
    for ticker in tickers:
        sym_list += "&symbol="+ticker+"|stocks"
    api = GET_STATS_API+sym_list
    data = get_url (api)
    if data:
        log.debug ("ticker %s, total-number (%d)"%(pprint.pformat(data), len(data)))
        return data["data"]
            
######### ******** MAIN ****** #########
if __name__ == '__main__':
    '''
    main entry point
    '''
    getcontext().prec = 8  # decimal precision
    print("Starting Wolfinch Screener..")
    try:
        log.info("Starting Main")
        print("Starting Main")
        get_tickers_stats(["AAPL", "csco"])
    except(KeyboardInterrupt, SystemExit):
        sys.exit()
    except Exception as e:
        log.critical("Unexpected error: exception: %s" %(traceback.format_exc()))
        print("Unexpected error: exception: %s" %(traceback.format_exc()))
        raise
#         traceback.print_exc()
#         os.abort()
    # '''Not supposed to reach here'''
    print("\nNasdaq end")

# EOF
