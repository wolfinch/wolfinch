'''
 SkateBot Auto trading Bot
 Desc: Gdax exchange interactions
 (c) Joshith
'''
import requests
import json
import pprint

import gdax as GDAX
from utils import *
from pstats import add_callers
from market import Market

__name__ = "gdax"

log = getLogger ('GDAX')

# Globals
gdax_conf = {}
gdax_products = []
gdax_accounts = {}
public_client = None
auth_client   = None
ws_client = None

#GDAX CONFIG FILE
GDAX_CONF = 'exchanges/gdaxClient/config.yml'

def market_init (exchange, product):
    usd_acc = gdax_accounts['USD']
    crypto_acc = gdax_accounts.get(product['base_currency'])
    if (usd_acc == None or crypto_acc == None): 
        log.error ("No account available for product: %s"%(product['id']))
        return None
    #Setup the initial params
    market = Market(product=product, exchange=exchange)    
    market.fund.set_initial_value(usd_acc['available'])
    market.fund.set_hold_value(usd_acc['hold'])
    market.fund.set_fund_liquidity_percent(10)       #### Limit the fund to 10%
    market.fund.set_max_per_buy_fund_value(100)
    market.crypto.set_initial_size( crypto_acc['available'])
    market.crypto.set_hold_size( crypto_acc['hold'])
    return market

def init():
    log.info('init GDAX params')
    global gdax_conf, public_client, auth_client
    
    conf = readConf (GDAX_CONF)
    if (conf != None and len(conf)):
        gdax_conf = conf['exchange']
    else:
        return False
    
    public_client = GDAX.PublicClient()
    if (public_client) == None :
        log.critical("gdax public client init failed")
        return False
    
    key = gdax_conf.get('apiKey')
    b64secret = gdax_conf.get('apiSecret')
    passphrase = gdax_conf.get('apiPassphrase')
    api_base = gdax_conf.get ('apiBase')
    
    if ((key and b64secret and passphrase and api_base ) == False):
        log.critical ("Invalid API Credentials in GDAX Config!! ")
        return False
    
    auth_client = GDAX.AuthenticatedClient(key, b64secret, passphrase,
                                  api_url=api_base)
    
    if auth_client == None:
        log.critical("Unable to Authenticate with GDAX exchange. Abort!!")
        return False
    
    global gdax_products
    products = public_client.get_products()
    if (len(products) and len (gdax_conf['products'])):
        for prod in products:
            for p in gdax_conf['products']:              
                if prod['id'] in p.keys():
                    gdax_products.append(prod)
    
    # Popoulate the account details for each interested currencies
    accounts =  auth_client.get_accounts()
    if (accounts == None):
        log.critical("Unable to get account details!!")
        return False
    #log.debug ("Exchange Accounts: %s"%(pprint.pformat(accounts, 4)))
    for account in accounts:
        for prod in gdax_conf['products']:
            for prod_id in prod.keys():
                currency = prod[prod_id][0]['currency']            
                if account['currency'] in currency:
                    log.debug ("Interested Account Found for Currency: "+account['currency'])
                    gdax_accounts[account['currency']] = account
                    break
    
    log.info( "**GDAX init success**\n Products: %s\n Accounts: %s"%(
                    pprint.pformat(gdax_products, 4), pprint.pformat(gdax_accounts, 4)))
    return True


def get_product_order_book (product, level = 1):
    v = public_client.get_product_order_book(product, level)
    log.debug(v)
    return v

    
############ ************** Public APIs for Exchange *********** ###########    
    # def products():
#     api_base = gdax_conf['apiBase']
#     response = requests.get(api_base + '/products')
#     # check for invalid api response
#     if response.status_code is not 200:
#         raise Exception('Invalid GDAX Status Code: %d' % response.status_code)
#     #log.debug(response.json())
#     return response.json()

def get_products():
    """
    Get registered products on this exchange
    """
    #  log.debug(gdax_products)    
    return gdax_products
def get_accounts ():
#     log.debug (pprint.pformat(gdax_accounts))
    return gdax_accounts    
def buy (trade_req) :
    log.debug ("BUY - Placing Order on exchange --" )    
    order_id = auth_client.buy(price=trade_req['price'], #USD
                    size=trade_req['size'], #BTC
                    product_id=trade_req['product'],
                    type='limit',
                    post_only='True'                    
                    )
    return normalized_order (order_id);
def sell (trade_req) :
    log.debug ("SELL - Placing Order on exchange --" )    
    order_id = auth_client.buy(price=trade_req['price'], #USD
                    size=trade_req['size'], #BTC
                    product_id=trade_req['product'],
                    type='limit',
                    post_only='True'
                    )
    return normalized_order (order_id);
def normalized_order (order):
    '''
    Desc:
     Error Handle and Normalize the order json returned by gdax
      to return the normalized order detail back to callers
    Sample order:
            {u'created_at': u'2018-01-10T09:49:02.639681Z',
             u'executed_value': u'0.0000000000000000',
             u'fill_fees': u'0.0000000000000000',
             u'filled_size': u'0.00000000',
             u'id': u'7150b013-62ca-49c7-aa28-4a9473778644',
             u'post_only': True,
             u'price': u'14296.99000000',
             u'product_id': u'BTC-USD',
             u'settled': False,
             u'side': u'buy',
             u'size': u'0.13988959',
             u'status': u'pending',
             u'stp': u'dc',
             u'time_in_force': u'GTC',
             u'type': u'limit'}    
    Known Errors: 
      1. {u'message': u'request timestamp expired'}
      2. {u'message': u'Insufficient funds'}
      3. {'status' : 'rejected', 'reject_reason': 'post-only'}
    '''
    error_status_codes = ['rejected']
    log.debug ("Order Response:\n%s"%(pprint.pformat(order, 4)))
    
    msg = order.get('message')
    status = order.get('status')
    if (msg or (status in error_status_codes)):
        log.error("FAILED Order: error msg: %s status: %s"%(msg, status))
        return None

    # Success    //TODO: FIXME: jork: Do actual normalization as required
    return order
    
#EOF    