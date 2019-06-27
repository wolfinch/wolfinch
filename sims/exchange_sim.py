# '''
#  OldMonk Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''

# import requests
# import json
import uuid
import time
from datetime import datetime
# from dateutil.tz import tzlocal
import copy

from utils import getLogger
from market import feed_enQ, TradeRequest, Order


__name__ = "EXCH-SIMS"
log = getLogger (__name__)
log.setLevel (log.CRITICAL)

###### SIMULATOR Global switch ######
simulator_on = True
import_only = False

'''
Description: Exchange Simulation for papertrade/backtesting. 
             Works in conjunction with the regular exchange. 
    When Initialized with an exchange it handles the buy/sell
    order and handles the trade as if it is done on exchange based on the ticker value.
    Maintains a list of open orders and executed orders. 
     
'''

open_orders = {}
traded_orders = {}       # TODO: FIXME: jork:  use the order_book implementation when implemented

order_struct = {u'created_at': u'2018-01-10T09:49:02.639681Z',
             u'executed_value': u'0.0000000000000000',
             u'fill_fees': u'0.0000000000000000',
             u'filled_size': u'0.00000000',
             u'id': u'TESTUUID-62ca-49c7-aa28-TESTUUID',
             u'post_only': True,
             u'price': u'0.0',
             u'product_id': u'BTC-USD',
             u'settled': False,
             u'side': u'buy',
             u'size': u'0.0',
             u'status': u'',
             u'stp': u'dc',
             u'time_in_force': u'GTC',
             u'type': u'limit'}

####### Private #########
def do_trade (market):
    open_orders_pvt = open_orders.get(market.product_id) or []
    traded_orders_pvt = traded_orders.get(market.product_id) 
    if traded_orders_pvt == None:
        traded_orders_pvt = []
        traded_orders[market.product_id] = traded_orders_pvt
    
    price = market.get_market_rate()
    log.debug ("SIM EXH stats: open_orders : %d traded_orders: %d price: %s"%(
        len(open_orders_pvt), len(traded_orders_pvt), price))
    for order in open_orders_pvt[:]:
        #first update order state
        order.status_type = 'received'
#         print ("order: %s"%(str(order)))
        market.order_status_update (order)
        #now trade
        this_order = copy.deepcopy(order_struct) # Note: this at the top
        this_order['created_at'] = datetime.now().isoformat()
        this_order['product_id'] = market.product_id
        this_order['id'] = order.id
        this_order['type'] = "done"
        this_order['reason'] = 'filled'    
        this_order['settled'] = True
        this_order['side'] = order.side
        if order.order_type == 'limit':
            this_order['price'] = order.price
            this_order['size'] = order.request_size
            if order.side == 'buy':
                if order.price >= price:
                    feed_enQ(market, this_order)
                    traded_orders_pvt.append (order)
                    open_orders_pvt.remove (order)
                    log.info ("Traded Buy order: %s"%(str(order)))
            elif order.side == 'sell':
                if order.price <= price:
                    feed_enQ(market, this_order)
                    traded_orders_pvt.append (order)
                    open_orders_pvt.remove (order)
                    log.info ("Traded sell order: %s"%(str(order)))
        elif order.order_type == 'market':
            this_order['price'] = price            
            this_order['filled_size'] = order.request_size
            this_order['executed_value'] = order.funds
            feed_enQ(market, this_order)
            traded_orders_pvt.append (order)
            open_orders_pvt.remove (order)
            log.info ("\n\nTraded market order: %s filled_order: %s price: %s"%(str(order), str(this_order), str(price)))
    #end While(true)

############# Public APIs ######################
def market_simulator_run (market):
    log.debug ("Running SIM exchange for market: %s"%(market.product_id))
    do_trade (market)
        
def buy (trade_req) :
#     return None
    
    if not isinstance( trade_req, TradeRequest):
        return None
    log.debug ("BUY - Placing Order on SIM exchange --" )
    
    buy_order = Order(str(uuid.uuid1()), trade_req.product, "pending", order_type=trade_req.type, 
                      status_reason=None, side='buy', request_size=trade_req.size,
                   filled_size=0,  price=trade_req.price, funds=trade_req.fund,
                 fees=0, create_time=time.ctime())
    
    open_orders_pvt = open_orders.get(trade_req.product) 
    if open_orders_pvt == None:
        open_orders[trade_req.product] = [buy_order]
    else:
        open_orders_pvt.append(buy_order)
    
    return buy_order
    
def sell (trade_req) :
    if not isinstance(trade_req, TradeRequest):
        return None
    log.debug ("SELL - Placing Order on SIM exchange --" )
    sell_order = Order(str(uuid.uuid1()), trade_req.product, "pending", order_type=trade_req.type, 
                      status_reason=None, side='sell', request_size=trade_req.size,
                   filled_size=0,  price=trade_req.price, funds=0,
                 fees=0, create_time=time.ctime()) 
    open_orders_pvt = open_orders.get(trade_req.product) 
    if open_orders_pvt == None:
        open_orders[trade_req.product] = [sell_order]
    else:
        open_orders_pvt.append(sell_order)
    return sell_order
    
def get_order (order_id):
#     open_orders_pvt = open_orders.get(market.product_id)
#     for order in open_orders_pvt[:]:
#         if (order.id == order_id):
#             this_order = order_struct
#             this_order['id'] = order.id
#             this_order['type'] = "done"
#             this_order['reason'] = 'filled'    
#             this_order['settled'] = True
#             this_order['side'] = order.side            
    return None
        
#EOF
