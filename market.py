
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
log = logger.getLogger ('TRADE')

#simple class to have the trade request (FIXME: add proper shape)



class TradeRequest:
#          ''' 
#            class {
#            product:
#            type:
#            size:
#            price:
#            }
#         '''   
    def __init__(self, entries):
        self.__dict__.update(entries)
            
class Fund:
    def set_initial_value (self, value):
        self.initial_value = self.current_value = value
    def set_fund_liquidity_percent (self, value):
        self.fund_liquidity_percent = value
    def set_hold_value (self, value):
        self.current_hold_value = value      
    def set_max_per_buy_fund_value (self, value):
        self.max_per_buy_fund_value = value  
    def __init__(self):
        self.initial_value = None
        self.current_value = None
        self.current_hold_value = None
        self.total_traded_value = None
        self.current_realized_profit = None
        self.current_unrealized_profit = None   
        self.total_profit = None
        self.current_avg_buy_price = None
        self.latest_buy_price = None         
        self.fund_liquidity_percent = None
        self.max_per_buy_fund_value = None
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
    def add_or_update_order (self, order):
        order_id = uuid.UUID(order['id'])
        order_status = order['status']
        if (order['side'] == 'buy'):
            if (order_status == 'done'):
                #a previously placed order is completed, remove from open order, add to completed orderlist
                if (self.open_buy_orders_db.get(order_id)):
                    del (self.open_buy_orders_db[order_id])
                    self.total_open_order_num -=1
                self.traded_buy_orders_db.append(order)
            elif (order_status ==  'pending'): ####### TODO: FIXME: Add more conditions
                # this is a new order
                self.open_buy_orders_db[order_id] = order
                self.total_open_order_num +=1
                self.total_open_order_num +=1
            else:
                log.critical("UNKNOWN order status: %s"%(order_status ))                
                
        elif (order['side'] == 'sell'):
            if (order['status'] == 'done'):
                #a previously placed order is completed, remove from open order, add to completed orderlist
                if (self.open_sell_orders_db.get(order_id)):
                    del (self.open_sell_orders_db[order_id])
                    self.total_open_order_num -=1                    
                self.traded_sell_orders_db.append(order)
            elif (order_status ==  'pending'): ####### TODO: FIXME: Add more conditions
                # this is a new order
                self.open_sell_orders_db[order_id] = order
                self.total_open_order_num +=1
                self.total_open_order_num +=1
            else:
                log.critical("UNKNOWN order status: %s"%(order_status ))
                
    def __init__(self):
        self.total_order_num = 0
        self.total_open_order_num = 0        
        self.open_buy_orders_db = {}
        self.open_sell_orders_db = {}
        self.traded_buy_orders_db = []
        self.traded_sell_orders_db = []
    
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
#     '''    
    def __init__(self, product=None, exchange=None):
        self.product_id = None if product == None else product['id']
        self.name = None if product == None else product['display_name']
        self.exchange_name = None if exchange == None else exchange.__name__
        self.exchange = exchange       #exchange module
        self.fund = Fund ()
        self.crypto = Crypto ()
        self.orders = Orders ()
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
            trade_req = json.load(fp)
            #delete the file after reading to make sure multiple order from same orderfile
            os.remove(manual_file_name)
            # Validate
            if (trade_req != None and trade_req['product'] == market.product_id ):
                log.info("Valid manual order : ")
    else:
        log.info ("Find trade Volume")
        log.info ("Trade Signal strength:"+str(signal))         ## TODO: FIXME: IMPLEMENT:
        trade_req = generate_market_trade_req(market, signal)
    #validate the trade Req
    if (trade_req != None and trade_req['size'] > 0 and trade_req['price'] > 0):
        ## Now we have a proper trader request
        # Execute the trade request and retrieve the order # and store it
        execute_market_trade(market, trade_req)
def execute_market_trade(market, trade_req):
    '''
    Desc: Execute a trade request on the market. 
          This API calls the sell/buy APIs of the curresponding exchanges 
          and expects the order in uniform format
    '''
    log.debug ("Executing Trade Request:"+str(trade_req))
    if (trade_req['type'] == 'BUY'):
        order = market.exchange.buy (trade_req)
    elif (trade_req['type'] == 'SELL'):
        order = market.exchange.sell (trade_req)
    if (order == None):
        log.error ("Placing Order Failed!")
        return
    #Add the successful order to the db
    save_order (market, trade_req, order)
def save_order (market, trade_req, order):
    market.orders.add_or_update_order(order)
    db.db_add_or_update_order (market, trade_req['product'], order)
def generate_market_trade_req (market, signal):
    '''
    Desc: Consider various parameters and generate a trade request
    Algo: 
    '''
    log.debug ('Calculate trade Req')    

#EOF