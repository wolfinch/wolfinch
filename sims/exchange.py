# '''
#  SkateBot Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''

import requests
import json
import pprint
import uuid

from utils import *
from pstats import add_callers
from market import *

__name__ = "EXCH-SIMS"

log = getLogger ('EXCH-SIMS')

order_struct = {u'created_at': u'2018-01-10T09:49:02.639681Z',
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

def buy (trade_req) :
    log.debug ("BUY - Placing Order on exchange --" ) 
    buy_order = order_struct
    buy_order['id']  = str(uuid.uuid1())
    buy_order['side'] = 'buy'
    buy_order['sell_order'] = trade_req.price
    buy_order['size'] = trade_req.size
    return buy_order
    
def sell (trade_req) :
    log.debug ("SELL - Placing Order on exchange --" )  
    sell_order = order_struct
    sell_order['id']  = str(uuid.uuid1())    
    sell_order['side'] = 'sell'
    sell_order['price'] = trade_req.price
    sell_order['size'] = trade_req.size    
    return sell_order    
    