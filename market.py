
'''
 SkateBot Auto trading Bot
 Desc: Market/trading routines
 (c) Joshith Rayaroth Koderi
'''

import json
import os
import uuid

from utils import logger
import db
from itertools import product
from docutils.nodes import sidebar
log = logger.getLogger ('TRADE')

#simple class to have the trade request (FIXME: add proper shape)

class TradeRequest:
#          ''' 
#            class {
#            product: <name>
#            side: <BUY|SELL>
#            type: <limit|market>
#            size: <SIZE crypto>
#            price: <limit/market-price>
#            }
#         '''   
    def __init__(self, Product, Side, Size, Type, Price, Stop):
        self.product = Product
        self.side = Side
        self.size = Size
        self.type = Type
        self.price = Price
        self.stop = Stop
    def __str__(self):
        return "{'product':%s, 'side':%s, 'size':%g 'type':%s, 'price':%g, 'stop':%g}"%(
            self.product, self.side, self.size, self.type, self.price, self.stop)
        
class Fund:
    def set_initial_value (self, value):
        self.initial_value = self.current_value = float(value)
    def set_fund_liquidity_percent (self, value):
        self.fund_liquidity_percent = float(value)
    def set_hold_value (self, value):
        self.current_hold_value = float(value)      
    def set_max_per_buy_fund_value (self, value):
        self.max_per_buy_fund_value = float(value)  
    def __init__(self):
        self.initial_value = 0.0
        self.current_value = 0.0
        self.current_hold_value = 0.0
        self.total_traded_value = 0.0
        self.current_realized_profit = 0.0
        self.current_unrealized_profit = 0.0   
        self.total_profit = 0.0
        self.current_avg_buy_price = 0.0
        self.latest_buy_price = 0.0         
        self.fund_liquidity_percent = 0.0
        self.max_per_buy_fund_value = 0.0
    def __str__(self):
        return ("{'initial_value':%g,'current_value':%g,'current_hold_value':%g,"
                "'total_traded_value':%g,'current_realized_profit':%g,'current_unrealized_profit':%g"
                ",'total_profit':%g,'current_avg_buy_price':%g,'latest_buy_price':%g,"
                "'fund_liquidity_percent':%g, 'max_per_buy_fund_value':%g}")%(
            self.initial_value, self.current_value, self.current_hold_value,
             self.total_traded_value,self.current_realized_profit, 
             self.current_unrealized_profit, self.total_profit, self.current_avg_buy_price, 
             self.latest_buy_price, self.fund_liquidity_percent, self.max_per_buy_fund_value )
class Crypto:
    def set_initial_size (self, size):
        self.initial_size = self.current_size = size
    def set_hold_size (self, size):
        self.current_hold_size = size
    def __init__(self):    
        self.initial_size = 0.0
        self.current_size = 0.0
        self.latest_traded_size = 0.0
        self.current_hold_size = 0.0
        self.total_traded_size = 0.0                      
class Orders:
    def add_pending_trade_req(self, trade_req):
        self.pending_trade_req.append(trade_req)
    def remove_pending_trade_req(self, trade_req):
        #primitive 
        self.pending_trade_req.remove(trade_req)
        
    def add_or_update_order (self, order):
        if (not order):
            return False
        order_id = uuid.UUID(order['id'])
        order_status = order['status']
        if (order['side'] == 'buy'):
            if (order_status == 'done'):
                #a previously placed order is completed, remove from open order, add to completed orderlist
                if (self.open_buy_orders_db.get(order_id)):
                    del (self.open_buy_orders_db[order_id])
                    self.total_open_order_count -=1
                self.traded_buy_orders_db.append(order)
            elif (order_status ==  'pending'): ####### TODO: FIXME: Add more conditions
                # this is a new order
                self.open_buy_orders_db[order_id] = order
                self.total_open_order_count +=1
                self.total_order_count +=1
            else:
                log.critical("UNKNOWN buy order status: %s"%(order_status ))
                return False
        elif (order['side'] == 'sell'):
            if (order['status'] == 'done'):
                #a previously placed order is completed, remove from open order, add to completed orderlist
                if (self.open_sell_orders_db.get(order_id)):
                    del (self.open_sell_orders_db[order_id])
                    self.total_open_order_count -=1                    
                self.traded_sell_orders_db.append(order)
            elif (order_status ==  'pending'): ####### TODO: FIXME: Add more conditions
                # this is a new order
                self.open_sell_orders_db[order_id] = order
                self.total_open_order_count +=1
                self.total_order_count +=1
            else:
                log.critical("UNKNOWN sell order status: %s"%(order_status ))
                return False
        return True
    def __init__(self):
        self.total_order_count = 0
        self.total_open_order_count = 0        
        self.open_buy_orders_db = {}
        self.open_sell_orders_db = {}
        self.traded_buy_orders_db = []
        self.traded_sell_orders_db = []
        self.pending_trade_req = []           #TODO: FIXME: jork: this better be a nice AVL tree or sort
    
class Market:
#     '''
#     Initialize per exchange, per product data.
#     This is where we want to keep all the run stats
#     {
#      product_id :
#      product_name: 
#      exchange_name:
#      fund {
#      initial_value:   < Initial fund value >
#      current_value:
#      current_hold_value
#      total_traded_value:
#      current_realized_profit:
#      current_unrealized_profit
#      total_profit:
#      fund_liquidity_percent: <% of total initial fund allowed to use>     
#      max_per_buy_fund_value:
#      }
#      crypto {
#      initial_size:
#      current_size:
#      current_hold_size:
#      current_avg_value:
#      total_traded_size:
#      }
#      orders {
#      total_order_num
#      open_buy_orders_db: <dict>
#      open_sell_orders_db: <dict>
#      traded_buy_orders_db:
#      traded_sell_orders_db:
#      }
#     } 
#        trade_req
#         self.product = Product
#         self.side = Side
#         self.size = Size
#         self.type = Type
#         self.price = Price
#         
#     '''    
    def handle_pending_trades (self):
        #TODO: FIXME:jork: Might need to extend
        log.debug("(%d) Pending Trade Reqs "%(len(self.orders.pending_trade_req)))
        for trade_req in self.orders.pending_trade_req[:]:
            if (trade_req.side == 'BUY'):
                if (trade_req.stop >= self.current_market_rate):
                    self.buy_order_create(trade_req)
                    self.orders.remove_pending_trade_req(trade_req)
                else:
                    log.debug("STOP BUY: market(%g) higher than STOP (%g)"%(self.current_market_rate, trade_req.stop))
            elif (trade_req.side <= 'SELL'):
                if (trade_req.stop <= self.current_market_rate):
                    self.sell_order_create(trade_req)
                    self.orders.remove_pending_trade_req(trade_req)     
                else:
                    log.debug("STOP SELL: market(%g) lower than STOP (%g)"%(self.current_market_rate, trade_req.stop))                                   
            
    def buy_order_create (self, trade_req):
        order = self.exchange.buy (trade_req)
        #update fund 
        order_cost = (trade_req.size*trade_req.price)
        if(True == self.orders.add_or_update_order(order)): #successful order
            self.fund.current_hold_value += order_cost
            self.fund.current_value -= order_cost
    def buy_order_filled (self, order):
        if(True == self.orders.add_or_update_order(order)): #Valid order
            order_cost = (order['size']*order['price'])
            #fund
            self.fund.current_hold_value -= order_cost
            self.fund.latest_buy_price = order['price']
            self.fund.total_traded_value += order_cost
            #avg cost
            curr_total_crypto_size = (self.crypto.current_hold_size + self.crypto.current_size)
            self.fund.current_avg_buy_price = (((self.fund.current_avg_buy_price *
                                                  curr_total_crypto_size) + (order_cost))/
                                                        (curr_total_crypto_size + order['size']))
            #crypto
            self.crypto.current_size += order['size']
            self.crypto.latest_traded_size = order['size']
            self.crypto.total_traded_size += order['size']
    def buy_order_cancelled(self, order):
        if(True == self.orders.add_or_update_order(order)): #Valid order
            order_cost = (order['size']*order['price'])
            self.fund.current_hold_value -= order_cost
            self.fund.current_value += order_cost        
    def sell_order_create (self, trade_req):
        order = self.exchange.sell (trade_req)
        #update fund 
        if(True == self.orders.add_or_update_order(order)): #successful order
            self.crypto.current_hold_size += trade_req.size
            self.fund.current_size -= trade_req.size
    def sell_order_filled (self, order):
        if(True == self.orders.add_or_update_order(order)): #Valid order
            order_cost = (order['size']*order['price'])        
            #fund
            self.fund.current_value += order_cost
            #crypto
            self.crypto.current_hold_size -= order['size']
            #profit
            profit = (order['price'] - self.fund.current_avg_buy_price )*order['size']
            self.fund.current_realized_profit += profit
    def sell_order_cancelled(self, order):
        if(True == self.orders.add_or_update_order(order)): #Valid order
            self.crypto.current_hold_size -= order['size']
            self.crypto.current_size += order['size']
    def set_current_market_rate(self, value):
        self.current_market_rate = float(value)
    def __init__(self, product=None, exchange=None):
        self.product_id = None if product == None else product['id']
        self.name = None if product == None else product['display_name']
        self.exchange_name = None if exchange == None else exchange.__name__
        self.exchange = exchange       #exchange module
        self.current_market_rate = 0.0   
        self.fund = Fund ()
        self.crypto = Crypto ()
        self.orders = Orders ()
    def __str__(self):
        return "{'product_id':%s,'name':%s,'exchange_name':%s,'fund':%s,'crypto':%s,'orders':%s}"%(
                self.product_id,self.name,self.exchange_name, 
                str(self.fund), str(self.crypto), str(self.orders))
def execute_market_trade(market, trade_req_list):
#    print ("Market: %s"%(str(market)))
    '''
    Desc: Execute a trade request on the market. 
          This API calls the sell/buy APIs of the corresponding exchanges 
          and expects the order in uniform format
    '''
    for trade_req in trade_req_list:
        log.debug ("Executing Trade Request:"+str(trade_req))
        if (trade_req.type == 'limit'):
            if (trade_req.side == 'BUY'):
                order = market.buy_order_create (trade_req)
            elif (trade_req.side == 'SELL'):
                order = market.sell_order_create (trade_req)
            if (order == None):
                log.error ("Placing Order Failed!")
                return
            #Add the successful order to the db
            save_order (market, trade_req, order)
        elif (trade_req.type == 'stop'):
            #  Stop order, add to pending list
            log.debug("pending(stop) trade_req %s"%(str(trade_req)))
            market.orders.add_pending_trade_req(trade_req)
def save_order (market, trade_req, order):
    db.db_add_or_update_order (market, trade_req.product, order)
def generate_trade_request (market, signal):
    '''
    Desc: Consider various parameters and generate a trade request
    Algo: 
    '''
    log.debug ('Calculate trade Req')      
############## Public APIs ###############    
  

def update_market_states (market):
    '''
    Desc: 1. Update/refresh the various market states (rate, etc.)
          2. perform any pending trades (stop requests)
          3. Cancel/timeout any open orders if need be
    '''
    #1.update market states
    #2.
    #3.pending trades
    market.handle_pending_trades ()
    
def generate_trade_signal (market):
    """ 
    Do all the magic to generate the trade signal
    params : exchange, product
    return : trade signal (-5..0..5)
             -5 strong sell
             +5 strong buy
    """
    log.info ("Generate Trade Signal for product: "+market.product_id)
    
    signal = 0 
    
    ################# TODO: FIXME: jork: Implementation ###################
    
    return signal
def consume_trade_signal (market, signal):
    """
    Execute the trade based on signal 
     - Policy can be applied on the behavior of signal strength 
     Logic :-
     * Based on the Signal strength and fund balances, take trade decision and
        calculate the exact amount to be traded
         1.  See if there is any manual override, if there is one, that takes priority (skip other steps?)
         2.  el
         
         
        -- Manual Override file: "override/TRADE_<exchange_name>.<product>"
            Json format:
            {
             product : <ETH-USD|BTC-USD>
             type    : <BUY|SELL>
             size    : <BTC>
             price   : <limit-price>
            }
            
        -- To ignore a product
           add an empty file with name "<exchange_name>_<product>.ignore"
    """
    trade_req_list = []
    exchange_name = market.exchange.__name__
    ignore_file = "override/%s_%s.ignore"%(exchange_name, market.product_id)
    #Override file name = override/TRADE_<exchange_name>.<product>
    manual_file_name = "override/TRADE_%s.%s"%(exchange_name, market.product_id)
    if (os.path.isfile(ignore_file)):
        log.info("Ignore file present for product. Skip processing! "+ignore_file)
        return
    if os.path.isfile(manual_file_name):
        log.info ("Override file exists - "+manual_file_name)
        with open(manual_file_name) as fp:
            trade_req_dict = json.load(fp)
            #delete the file after reading to make sure multiple order from same orderfile
            os.remove(manual_file_name)
            # Validate
            if (trade_req_dict != None and trade_req_dict['product'] == market.product_id ):
                trade_req = TradeRequest(Product=trade_req_dict['product'],
                                          Side=trade_req_dict['side'],
                                           Size=trade_req_dict['size'],
                                            Type=trade_req_dict['type'],
                                             Price=trade_req_dict['price'],
                                             Stop=trade_req_dict['stop'])
                log.info("Valid manual order : %s"%(str(trade_req)))
                trade_req_list.append(trade_req)
    else:
        log.info ("Find trade Volume")
        log.info ("Trade Signal strength:"+str(signal))         ## TODO: FIXME: IMPLEMENT:
        trade_req = generate_trade_request(market, signal)
        trade_req_list.append(trade_req)
    #validate the trade Req
    if (trade_req != None and trade_req.size > 0 and trade_req.price > 0):
        ## Now we have a proper trader request
        # Execute the trade request and retrieve the order # and store it
        execute_market_trade(market, trade_req_list)    
#EOF