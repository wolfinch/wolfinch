# '''
#  SkateBot Auto trading Bot
#  Desc: Gdax exchange interactions
#  (c) Joshith
# '''

import requests
import json
import pprint
from decimal import Decimal

import gdax as GDAX #Official version seems to be old, doesn't support auth websocket client
#import third_party.gdax_python.gdax as GDAX
from utils import *
from pstats import add_callers
from market import *

__name__ = "gdax"

log = getLogger ('GDAX')
log.setLevel(log.DEBUG)

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
    global ws_client
    usd_acc = gdax_accounts['USD']
    crypto_acc = gdax_accounts.get(product['base_currency'])
    if (usd_acc == None or crypto_acc == None): 
        log.error ("No account available for product: %s"%(product['id']))
        return None
    #Setup the initial params
    market = Market(product=product, exchange=exchange)    
    market.fund.set_initial_value(Decimal(usd_acc['available']))
    market.fund.set_hold_value(Decimal(usd_acc['hold']))
    market.fund.set_fund_liquidity_percent(10)       #### Limit the fund to 10%
    market.fund.set_max_per_buy_fund_value(100)
    market.crypto.set_initial_size(Decimal( crypto_acc['available']))
    market.crypto.set_hold_size( Decimal(crypto_acc['hold']))
    
    ## Feed Cb
    market.consume_feed = gdax_consume_feed
    return market

def close ():
    log.debug("Closing exchange...")    
    global ws_client
    if (ws_client):
        log.debug("Closing WebSocket Client")
        ws_client.close ()

def init():
    global ws_client
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
    feed_base = gdax_conf.get ('wsFeed')
    
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
    
    # register websocket feed 
    ws_client = register_feed (api_key=key, api_secret=b64secret, api_passphrase=passphrase, url=feed_base)
    if ws_client == None:
        log.critical("Unable to get websocket feed. Abort!!")
        return False
    
    #Start websocket Feed Client
    if (ws_client != None):
        log.debug ("Starting Websocket Feed... ")
        ws_client.start()    
            
    log.info( "**GDAX init success**\n Products: %s\n Accounts: %s"%(
                    pprint.pformat(gdax_products, 4), pprint.pformat(gdax_accounts, 4)))
    return True

def normalized_order (order):
    '''
    Desc:
     Error Handle and Normalize the order json returned by gdax
      to return the normalized order detail back to callers
      Handles -
      1. Initial Order Creation/Order Query
      2. Order Update Feed Messages
      Ref: https://docs.gdax.com/#the-code-classprettyprintfullcode-channel
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
    log.debug ("Order msg:\n%s"%(pprint.pformat(order, 4)))
    
    msg = order.get('message')
    status = order.get('status')
    if (msg or (status in error_status_codes)):
        log.error("FAILED Order: error msg: %s status: %s"%(msg, status))
        return None

    # Valid Order
    product_id = order.get('product_id')
    order_id   = order.get('id') or order.get('order_id')
    order_type = order.get('type')
    status_reason = order.get('reason')
    status_type = order.get('status') 
    if order_type in ['received', 'open', 'done', 'match', 'change', 'margin_profile_update', 'activate' ]:
        # order status update message
        status_type = order_type
        order_type = order.get('order_type') #could be None
    else:
        pass
    create_time = order.get('created_at') or None
    modify_time  = order.get('time') or None
    side = order.get('side') or None
    price =   Decimal(order.get('price') or -1)
    size  = Decimal(order.get('size') or -1)
    remainig_size  = Decimal(order.get('remaining_size') or -1)
    funds = Decimal(order.get('funds') or -1)
    
    norm_order = Order (order_id, product_id, status_type, order_type=order_type, status_reason=status_reason,
                        side=side, size=size, remainig_size=remainig_size, price=price, funds=funds, create_time=create_time, modify_time=modify_time)
    return norm_order

######### WebSocket Client implementation #########

class gdaxWebsocketClient (GDAX.WebsocketClient):
#     __init__(self, url="wss://ws-feed.gdax.com", products=None, message_type="subscribe", mongo_collection=None,
#                  should_print=True, auth=False, api_key="", api_secret="", api_passphrase="", channels=None):
        def on_open(self):
            #self.url = "wss://ws-feed.gdax.com/"
            self.message_count = 0
            print("Let's count the messages!")

        def on_message(self, msg):
            self.feed_enQ_msg (msg)
            #print(json.dumps(msg, indent=4, sort_keys=True))
            self.message_count += 1

        def on_close(self):
            print("-- Goodbye! --")
        def feed_enQ_msg (self, msg):
            #print("Feed MSG: %s"%(json.dumps(msg, indent=4, sort_keys=True)))     
            msg_type = msg.get('type') 
            product_id = msg.get("product_id")
            if (msg_type == 'ticker'):
                if (product_id == None):
                    log.error ("Feed Thread: Invalid Product-id: %s"%(json.dumps(msg, indent=4, sort_keys=True)))
                    return
                market = get_market_by_product (product_id)
                if (market == None):
                    log.error ("Feed Thread: Unknown market: %s"%(json.dumps(msg, indent=4, sort_keys=True)))
                    return                
                feed_enQ(market, msg)
            elif (msg_type == 'snapshot') or (msg_type == 'l2update'):
                if (product_id == None):
                    log.error ("Feed Thread: Invalid Product-id: %s"%(json.dumps(msg, indent=4, sort_keys=True)))
                    return
                market = get_market_by_product (product_id)
                if (market == None):
                    log.error ("Feed Thread: Unknown market: %s"%(json.dumps(msg, indent=4, sort_keys=True)))
                    return                
                feed_enQ(market, msg)
            elif (msg_type == 'received' or msg_type == 'open' or
                  msg_type == 'done' or msg_type == 'match' or msg_type == 'change' ):    
                if (product_id == None):
                    log.error ("Feed Thread: Invalid Product-id: %s"%(json.dumps(msg, indent=4, sort_keys=True)))
                    return
                market = get_market_by_product (product_id)
                if (market == None):
                    log.error ("Feed Thread: Unknown market: %s"%(json.dumps(msg, indent=4, sort_keys=True)))
                    return                  
                feed_enQ(market, msg)           
            elif (msg_type == 'heartbeat'):
                log.debug ("Feed Thread: Heartbeat")
            elif (msg_type == 'subscriptions'):          
                log.info ("Feed: Subscribed to WS feed %s"%(json.dumps(msg, indent=4, sort_keys=True)))
            elif (msg_type == 'error'):
                log.error ("Feed Thread: Error Msg received on Feed msg: %s"%(json.dumps(msg, indent=4, sort_keys=True)))
            else:
                log.error ("Feed Thread: Unknown Feed Msg Type (%s)"%(msg['type']))
    
def register_feed (api_key="", api_secret="", api_passphrase="", url=""):
    products = ["BTC-USD", "ETH-USD"]
    channels = [
            "level2",
            "heartbeat",
            "ticker",
            "user"         #Receive details about our orders only
        ]
    message_type = "subscribe"
    websocket_client = gdaxWebsocketClient (url, products=products, message_type=message_type,
                                            should_print=False, auth=True,
                                            api_key=api_key, api_secret=api_secret,
                                             api_passphrase=api_passphrase, channels=channels)
    if websocket_client == None:
        log.error ("Unable to register websocket client")
        return None
    else:
        log.debug ("Initialized websocket client")        
        return websocket_client

######## Feed Consume #######
def gdax_consume_feed (market, msg):
    ''' 
    Feed Call back for Gdax    
    This is where we do all the useful stuff with Feed
    '''
    msg_type = msg['type']
    #log.debug ("Feed received: msg:\n %s"%(json.dumps(msg, indent=4, sort_keys=True)))
    if (msg_type == 'ticker'):
        gdax_consume_ticker_feed (market, msg)
    elif (msg_type == 'heartbeat'):
        log.debug ("Feed: Heartbeat")
    elif (msg_type == 'snapshot'):
        gdax_consume_l2_book_snapshot (market, msg)
    elif (msg_type == 'l2update'):
        gdax_consume_l2_book_update (market, msg)        
    elif (msg_type == 'received' or msg_type == 'open' or
           msg_type == 'done' or msg_type == 'match' or msg_type == 'change' ):
        gdax_consume_order_update_feed (market, msg)
    elif (msg_type == 'error'):
        log.error ("Feed: Error Msg received on Feed msg: %s"%(json.dumps(msg, indent=4, sort_keys=True)))
    else:
        log.error ("Feed: Unknown Feed Msg Type (%s) msg: %s"%(msg['type'], json.dumps(msg, indent=4, sort_keys=True)))

def gdax_consume_order_update_feed (market, msg):
    ''' 
    Process the order status update feed msg 
    '''
    log.debug ("Order Status Update id:%s"%(msg.get('order_id')))
    order = normalized_order(msg)
    market.order_status_update (order)

    
def gdax_consume_l2_book_snapshot (market, msg):
    '''
     Consume the OrderBook Snapshot and build orderbook
    '''    
    bids = msg ['bids'] or []
    asks = msg ['asks'] or []
    log.debug ("Building orderbook from snapshot for (%s): num_bids(%d) num_asks (%d) "%(
        market.name, len(bids), len(asks)))
    market.order_book.new_book (bids, asks)
    
def gdax_consume_l2_book_update (market, msg):
    '''
    {
        "type": "l2update",
        "product_id": "BTC-EUR",
        "changes": [
            ['side', 'price', 'size']
            ["buy", "1", "3"],
            ["sell", "3", "1"],
            ["sell", "2", "2"],
            ["sell", "4", "0"]
        ]
    }
    '''
    log.debug ("Updating L2 order book")
    changes = msg['changes'] or []
    for change in changes:
        side = change[0]
        price = change [1]
        size = change[2]
        if (side == 'buy'):
            market.order_book.add_bids([[price, size]])
        elif (size == 'sell'):
            market.order_book.add_asks([[price, size]])            
        
def gdax_consume_ticker_feed (market, msg):
    '''
    {
        "best_ask": "11367.87", 
        "best_bid": "11366.44", 
        "high_24h": "12019.44000000", 
        "last_size": "0.01000000", 
        "low_24h": "11367.87000000", 
        "open_24h": "10896.04000000", 
        "price": "11367.87000000", 
        "product_id": "BTC-USD", 
        "sequence": 3000902, 
        "side": "buy", 
        "time": "2018-01-19T09:53:02.816000Z", 
        "trade_id": 566669, 
        "type": "ticker", 
        "volume_24h": "264992.94231824", 
        "volume_30d": "364800.84143217"
    }
    '''
    log.debug ("Ticker Feed:%s"%(json.dumps(msg, indent=4, sort_keys=True)))
    
    #update ticker
    #TODO: FIXME: jork: might need to rate-limit the logic here after
    market.set_market_price (Decimal(msg['price']))
    market.handle_pending_trades()
    
    
    
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

def get_product_order_book (product, level = 1):
    '''
    Get the order book at specified level
    '''
    v = public_client.get_product_order_book(product, level)
    #log.debug(v)
    return v


def get_accounts ():
#     log.debug (pprint.pformat(gdax_accounts))
    return gdax_accounts    
def buy (trade_req) :
    log.debug ("BUY - Placing Order on exchange --" )    
    order_id = auth_client.buy(price=trade_req.price, #USD
                    size=trade_req.size, #BTC
                    product_id=trade_req.product,
                    type='limit',
                    post_only='True'                    
                    )
    return normalized_order (order_id);
def sell (trade_req) :
    log.debug ("SELL - Placing Order on exchange --" )    
    order_id = auth_client.buy(price=trade_req.price, #USD
                    size=trade_req.size, #BTC
                    product_id=trade_req.product,
                    type='limit',
                    post_only='True'
                    )
    return normalized_order (order_id);

#EOF    