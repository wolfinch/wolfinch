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

from binance.client import Client

log = getLogger ('Binance')
log.setLevel(log.DEBUG)

#BINANCE CONFIG FILE
BINANCE_CONF = 'exchanges/binance/config.yml'

class Binance (Exchange):
    name = "binance"
    binance_conf = {}
    binance_products = []
    binance_accounts = {}
    public_client = None
    auth_client   = None
    ws_client = None    
    def __init__ (self):
        log.info ("Init Binance exchange")
        
        conf = readConf (BINANCE_CONF)
        if (conf != None and len(conf)):
            self.binance_conf = conf['exchange']
        else:
            return None
        
        #get config
        backfill = self.binance_conf.get('backfill')
        if not backfill:
            log.fatal("Invalid Config file")
            return None
    
        for entry in backfill:
            if entry.get('enabled'):
                self.binance_conf['backfill_enabled'] = entry['enabled']
            if entry.get('period'):
                self.binance_conf['backfill_period'] = int(entry['period'])
            if entry.get('granularity'):
                self.binance_conf['backfill_granularity'] = int(entry['granularity'])            
            
        
        # for public client, no need of api key
        self.public_client = Client("", "")
        if (self.public_client) == None :
            log.critical("binance public client init failed")
            return None
        
        key = self.binance_conf.get('apiKey')
        b64secret = self.binance_conf.get('apiSecret')


        feed_base = self.binance_conf.get ('wsFeed')
        
        if ((key and b64secret ) == False):
            log.critical ("Invalid API Credentials in binance Config!! ")
            return None
        
        self.auth_client = Client(key, b64secret)
        
        if self.auth_client == None:
            log.critical("Unable to Authenticate with binance exchange. Abort!!")
            return None
            
#         global binance_products
        products = self.public_client.get_exchange_info()
        log.debug ("products: ",products)
        if (len(products) and len (self.binance_conf['products'])):
            for prod in products:
                for p in self.binance_conf['products']:              
                    if prod['id'] in p.keys():
                        self.binance_products.append(prod)
        
        # Popoulate the account details for each interested currencies
        accounts =  self.auth_client.get_accounts()
        if (accounts == None):
            log.critical("Unable to get account details!!")
            return False
        #log.debug ("Exchange Accounts: %s"%(pprint.pformat(accounts, 4)))
        for account in accounts:
            for prod in self.binance_conf['products']:
                for prod_id in prod.keys():
                    currency = prod[prod_id][0]['currency']            
                    if account['currency'] in currency:
                        log.debug ("Interested Account Found for Currency: "+account['currency'])
                        self.binance_accounts[account['currency']] = account
                        break
        
        # register websocket feed 
        self.ws_client = self._register_feed (api_key=key, api_secret=b64secret, api_passphrase=passphrase, url=feed_base)
        if self.ws_client == None:
            log.critical("Unable to get websocket feed. Abort!!")
            return None
        
        #Start websocket Feed Client
        if (self.ws_client != None):
            log.debug ("Starting Websocket Feed... ")
            self.ws_client.start()    
                
        log.info( "**CBPRO init success**\n Products: %s\n Accounts: %s"%(
                        pprint.pformat(self.binance_products, 4), pprint.pformat(self.binance_accounts, 4)))        
        
        
        
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

######### ******** MAIN ****** #########
if __name__ == '__main__':
    
    print ("Testing Binance exch:")
    
    
#EOF    
