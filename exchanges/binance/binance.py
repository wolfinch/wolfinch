# '''
#  OldMonk Auto trading Bot
#  Desc: Binance exchange interactions for OldMonk
#  (c) Joshith
# '''

import json
import pprint
from decimal import Decimal
from datetime import datetime, timedelta
from time import sleep
import time

from utils import getLogger, readConf
from market import Market, OHLC, feed_enQ, get_market_by_product, Order
from exchanges import Exchange

log = getLogger ('Binance')
log.setLevel(log.DEBUG)

class Binance (Exchange):
    
    name = "Binance"
    def __init__ (self):
        log.info ("Init Binance exchange")
    def __str__ (self):
        return "{Message: Binance Exchange }"
    
    def market_init (self):
        pass
    def close (self):
        pass    
    
    def buy (self):
        pass
    def sell (self):
        pass
    def get_order (self):
        pass
    def cancel_order (self):
        pass
    def get_products (self):
        return []
    
    def get_accounts (self):
        pass     
    def get_historic_rates (self):
        pass        
    def get_product_order_book (self):
        pass  

#EOF    
