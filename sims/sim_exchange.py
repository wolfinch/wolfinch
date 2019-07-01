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
from decimal import Decimal

from utils import getLogger
import exchanges
from market import feed_enQ, TradeRequest, Order, Market


__name__ = "EXCH-SIMS"
log = getLogger (__name__)
log.setLevel (log.CRITICAL)

###### SIMULATOR Global switch ######
simulator_on = True
import_only = False
exch_obj = None

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
        
class SIM_EXCH (exchanges.Exchange):
    products = []
    primary = False
    candle_interval = 0
    def __init__(self, name, primary=True):
        log.info('init SIM exchange')        
        
        self.name = name
        self.primary = True if primary else False
        self.timeOffset = 0

#         global products
        prod = {"id": "BTC-USD", "display_name": "BTC/USD"}
        self.products.append(prod)
        
    def market_init (self, product):
        #Setup the initial params
        market = Market(product=product, exchange=self)
                
        #Setup the initial params
        self._set_initial_acc_values (market)
        
        ## Init Exchange specific private state variables
        market.O = market.H = market.L = market.C = market.V = 0
        market.candle_interval = self.candle_interval = 300
        
        #set whether primary or secondary
        market.primary = self.primary
        
        market.register_feed_processor(self._sim_exch_consume_feed)
        return market

    def _sim_exch_consume_feed (self, market, msg):
        ''' 
        Feed Call back for SIM EXCH    
        This is where we do all the useful stuff with Feed
        '''
        msg_type = msg['type']
        #log.debug ("Feed received: msg:\n %s"%(json.dumps(msg, indent=4, sort_keys=True)))
     
        if (msg_type in ['pending', 'received' , 'open' , 'done' , 'change'] ):
            self._consume_order_update_feed (market, msg)
        elif (msg_type == 'error'):
            log.error ("Feed: Error Msg received on Feed msg: %s"%(str(msg)))
        else:
            log.error ("Feed: Unknown Feed Msg Type (%s) msg: %s"%(msg['type'], str(msg)))
    
    def _consume_order_update_feed (self, market, msg):
        ''' 
        Process the order status update feed msg 
        '''
        log.debug ("Order Status Update id:%s"%(msg.get('order_id')))
        order = self._normalized_order(msg)
        market.order_status_update (order)
        
    def _normalized_order (self, order):
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
        
        msg = order.get('message')
        status = order.get('status')
        if (msg or (status in error_status_codes)):
            log.error("FAILED Order: error msg: %s status: %s"%(msg, status))
            return None
    
        # Valid Order
        product_id = order.get('product_id')
        order_id   = order.get('id') or order.get('order_id')
        order_type = order.get('type')
        status_reason = order.get('reason') or order.get('done_reason')
        status_type = order.get('status') 
        if order_type in ['received', 'open', 'done', 'match', 'change', 'margin_profile_update', 'activate' ]:
            # order status update message
            status_type = order_type
            order_type = order.get('order_type') #could be None
        else:
            pass
        create_time = order.get('created_at') or None
        update_time  = order.get('time') or order.get('done_at') or None
        side = order.get('side') or None
        # Money matters
        price =   Decimal(order.get('price') or 0)
        request_size  = Decimal(order.get('size') or  0)    
        filled_size = Decimal(order.get('filled_size') or 0)
        remaining_size  = Decimal(order.get('remaining_size') or 0)
        funds = Decimal(order.get('funds') or order.get('specified_funds') or 0)
        fees = Decimal(order.get('fees') or order.get('fill_fees') or 0)
        if order.get('settled') == True:
            total_val = Decimal(order.get('executed_value') or 0)
            if total_val and filled_size and not price:
                price = total_val/filled_size
            if (funds == 0):
                funds = total_val + fees
                #log.debug ("calculated fill price: %g size: %g"%(price, filled_size))
    #         if filled_size and remaining_size:
    #             request_size = filled_size + remaining_size
                        
        if (request_size == 0):
            request_size = remaining_size + filled_size
            
        log.debug ("price: %g fund: %g req_size: %g filled_size: %g remaining_size: %g fees: %g"%(
            price, funds, request_size, filled_size, remaining_size, fees))
        norm_order = Order (order_id, product_id, status_type, order_type=order_type, status_reason=status_reason,
                            side=side, request_size=request_size, filled_size=filled_size, remaining_size=remaining_size,
                             price=price, funds=funds, fees=fees, create_time=create_time, update_time=update_time)
        return norm_order
        
    def _set_initial_acc_values (self, market):
        #Setup the initial params
        market.fund.set_fee(0.25, 0.15)            
        market.fund.set_initial_value(Decimal(2000))
    #     market.fund.set_hold_value(Decimal(100))
        market.fund.set_fund_liquidity_percent(90)       #### Limit the fund to 90%
        market.fund.set_max_per_buy_fund_value(90)
        market.asset.set_initial_size(Decimal(1))
        market.asset.set_hold_size( Decimal(0.1))
        market.asset.set_max_per_trade_size(Decimal(0.01))
            
    def close (self):
        log.debug("Closing SIM exchange...")
        
    def get_products(self):
        """
        Get registered products on this exchange
        """
        return self.products
                          
    def buy (self, trade_req) :
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
        
    def sell (self, trade_req) :
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
        
    def get_order (self, order_id):
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

    def cancel_order (self):
        pass

    def get_accounts (self):
        pass     

    def get_historic_rates (self):
        pass        

    def get_product_order_book (self):
        pass 
#EOF
