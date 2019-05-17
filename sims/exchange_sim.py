# '''
#  OldMonk Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''

# import requests
# import json
import uuid
import time
from decimal import Decimal

from utils import getLogger
from market import *
#from market.order import Order, TradeRequest
#from market import feed_enQ

__name__ = "EXCH-SIMS"
log = getLogger (__name__)
log.setLevel (log.INFO)

###### SIMULATOR Global switch ######
simulator_on = True
backtesting_on = False
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
             u'id': u'7150b013-62ca-49c7-aa28-4a9473778644',
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
        this_order = order_struct # Note: this at the top
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
            log.debug ("Traded market order: %s filled_order: %s price: %s"%(str(order), str(this_order), str(price)))
        
def set_initial_acc_values (market):
    #Setup the initial params
    market.fund.set_initial_value(Decimal(2000))
#     market.fund.set_hold_value(Decimal(100))
    market.fund.set_fund_liquidity_percent(90)       #### Limit the fund to 90%
    market.fund.set_max_per_buy_fund_value(50)
    market.asset.set_initial_size(Decimal(10))
    market.asset.set_hold_size( Decimal(0.1))
    market.asset.set_max_per_trade_size(Decimal(0.01))
        
def finish_backtesting(market):
    log.info ("finish backtesting. market:%s"%(market.name))

    # sell acquired assets and come back to initial state
    market.close_all_positions()
    return True
    
def do_backtesting ():
    # don't sleep for backtesting    
    sleep_time = 0
    done = False
    all_done = 0
        
    for market in get_market_list():
        log.info ("backtest setup for market: %s num_candles:%d"%(market.name, market.num_candles))
        market.backtesting_idx = 0
        set_initial_acc_values(market)        
                          
    while (all_done < 5) : 
        # check for the msg in the feed Q and process, with timeout
        done = True
        msg = feed_deQ(sleep_time)
        while (msg != None):
            feed_Q_process_msg (msg)
            msg = feed_deQ(0)        
        for market in get_market_list():
            market.update_market_states()
            # Trade only on primary markets
            if (market.primary == True and (market.backtesting_idx < market.num_candles)):
#                 log.info ("BACKTEST(%d): processing on market: exchange (%s) product: %s"%(
#                     market.backtesting_idx, market.exchange_name, market.name))     
                signal = market.generate_trade_signal (market.backtesting_idx)
                market.consume_trade_signal (signal)
                if (simulator_on):
                    market_simulator_run (market)
                #if atleast one market is not done, we will continue
                done = False
                market.backtesting_idx += 1
            elif done == True:
                finish_backtesting(market)
                market.backtesting_idx = market.num_candles - 1
                if (simulator_on):
                    market_simulator_run (market)                
                #let's do few iterations and make sure everything is really done!
                all_done += 1 
                       
    #end While(true)
def show_stats ():
    flush_all_stats()

############# Public APIs ######################
def market_simulator_run (market):
    log.debug ("Running SIM exchange for market: %s"%(market.product_id))
    do_trade (market)
        
def market_backtesting_run ():
    """
    market backtesting 
    """
    log.debug("starting backtesting")    
    do_backtesting()
    log.info ("backtesting complete. ")
    show_stats ()

    
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
