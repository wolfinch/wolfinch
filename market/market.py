
'''
 OldMonk Auto trading Bot
 Desc: Market/trading routines
 (c) Joshith Rayaroth Koderi
'''
##############################################
###### Bugs/Caveats, TODOs, AIs###############
### 1. Account Remaining_size for fund calculations
### 2. Use Fee and enhance to maker/taker fees


##############################################

import json
import os
import uuid
import Queue
import pprint
from itertools import product
from decimal import Decimal

from utils import *
from order_book import OrderBook
from order import TradeRequest
import db
import sims
import indicators
import strategy

log = getLogger ('MARKET')
log.setLevel(log.DEBUG)

OldMonk_market_list = []

class Fund:
    def __init__(self):
        self.initial_value = Decimal(0.0)
        self.current_value = Decimal(0.0)
        self.current_hold_value = Decimal(0.0)
        self.total_traded_value = Decimal(0.0)
        self.current_realized_profit = Decimal(0.0)
        self.current_unrealized_profit = Decimal(0.0)   
        self.total_profit = Decimal(0.0)
        self.current_avg_buy_price = Decimal(0.0)
        self.latest_buy_price = Decimal(0.0)         
        self.fund_liquidity_percent = Decimal(0.0)
        self.max_per_buy_fund_value = Decimal(0.0)
            
    def set_initial_value (self, value):
        self.initial_value = self.current_value = Decimal(value)
        
    def set_fund_liquidity_percent (self, value):
        self.fund_liquidity_percent = Decimal(value)
        
    def set_hold_value (self, value):
        self.current_hold_value = Decimal(value)      
        
    def set_max_per_buy_fund_value (self, value):
        self.max_per_buy_fund_value = Decimal(value)  

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
    def __init__(self):    
        self.initial_size = Decimal(0.0)
        self.current_size = Decimal(0.0)
        self.latest_traded_size = Decimal(0.0)
        self.current_hold_size = Decimal(0.0)
        self.total_traded_size = Decimal(0.0)
            
    def set_initial_size (self, size):
        self.initial_size = self.current_size = size
        
    def set_hold_size (self, size):
        self.current_hold_size = size

    def __str__(self):
        return ("{'initial_size':%g, 'current_size':%g, 'latest_traded_size':%g,"
                " 'current_hold_size':%g, 'total_traded_size':%g}")%(
            self.initial_size, self.current_size, self.latest_traded_size,
            self.current_hold_size, self.total_traded_size)
                
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
    def __init__(self, product=None, exchange=None):
        self.product_id = None if product == None else product['id']
        self.name = None if product == None else product['display_name']
        self.exchange_name = None if exchange == None else exchange.__name__
        self.exchange = exchange       #exchange module
        self.current_market_rate = Decimal(0.0)
        self.consume_feed = None
        self.fund = Fund ()
        self.crypto = Crypto ()
        #self.order_book = Orders ()
        self.order_book = OrderBook(market=self)
        # Market Strategy related Data
        # [{'ohlc':(time, open, high, low, close, volume), 'sma':val, 'ema', val, name:val...}]
        self.market_indicators_data     = [] 
        self.indicator_calculators     = indicators.Configure()
        self.market_strategies     = strategy.market_strategies
        
    def set_market_rate (self, price):
        self.current_market_rate = price
        
    def get_market_rate (self):
        return self.current_market_rate       
        
    def market_consume_feed(self, msg):
        if (self.consume_feed != None):
            self.consume_feed(self, msg)
            
    def _handle_pending_trades (self):
        #TODO: FIXME:jork: Might need to extend
        log.debug("(%d) Pending Trade Reqs "%(len(self.order_book.pending_trade_req)))

        if 0 == len(self.order_book.pending_trade_req):
            return 
        market_price = self.get_market_price()
        for trade_req in self.order_book.pending_trade_req[:]:
            if (trade_req.side == 'BUY'):
                if (trade_req.stop >= market_price):
                    self.buy_order_create(trade_req)
                    self.order_book.remove_pending_trade_req(trade_req)
                else:
                    log.debug("STOP BUY: market(%g) higher than STOP (%g)"%(self.current_market_rate, trade_req.stop))
            elif (trade_req.side <= 'SELL'):
                if (trade_req.stop <= market_price):
                    self.sell_order_create(trade_req)
                    self.order_book.remove_pending_trade_req(trade_req)     
                else:
                    log.debug("STOP SELL: market(%g) lower than STOP (%g)"%(self.current_market_rate, trade_req.stop))                                   
            
    def order_status_update (self, order):
        log.debug ("ORDER UPDATE: %s"%(str(order)))        
        
        side = order.side
        msg_type = order.status_type
        reason = order.status_reason
        if side == 'buy':
            if msg_type == 'done':
                #for an order done, get the order details
                order_det = self.exchange.get_order(order.id)
                if (order_det):
                    order = order_det
                if reason == 'filled':
                    self._buy_order_filled ( order)
                elif reason == 'canceled':
                    self._buy_order_canceled (order)
            elif msg_type == 'received':
                self._buy_order_received(order)
            elif (msg_type in ['open', 'match', 'change', 'margin_profile_update', 'activate' ]):
                log.debug ("Ignored buy order status: %s"%(msg_type))
            else:
                log.error ("Unknown buy order status: %s"%(msg_type))
        elif side == 'sell':
            if msg_type == 'done':
                #for an order done, get the order details
                order_det = self.exchange.get_order(order.id)
                if (order_det):
                    order = order_det                
                if reason == 'filled':
                    self._sell_order_filled ( order)
                elif reason == 'canceled':
                    self._sell_order_canceled (order)
            elif msg_type == 'received':
                self._sell_order_received(order)
            elif (msg_type in ['open', 'match', 'change', 'margin_profile_update', 'activate']):
                log.debug ("Ignored sell order status: %s"%(msg_type))
            else:
                log.error ("Unknown sell order status: %s"%(msg_type))
        else:
            log.error ("Unknown order Side (%s)"%(side))
                    
    def _buy_order_received (self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #successful order
            #update fund 
            order_type = market_order.order_type
            order_cost = 0
            if order_type == 'market':
                order_cost = Decimal(market_order.funds) 
            elif order_type == 'limit':
                order_cost = Decimal (market_order.price) * Decimal (market_order.request_size)
            else:
                log.error ("BUY: unknown order_type: %s"%(order_type))
                return
            self.fund.current_hold_value += order_cost
            self.fund.current_value -= order_cost
                                        
    def _buy_order_create (self, trade_req):
        if (sims.simulator_on):
            order = sims.buy (trade_req)
        else:
            order = self.exchange.buy (trade_req)
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #successful order
            log.debug ("BUY Order Sent to exchange. ")      
            return market_order
        else:
            log.debug ("BUY Order Failed to place")
            return None
            
    def _buy_order_filled (self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #Valid order          
            order_cost = (market_order.filled_size*market_order.price)
            #fund
            self.fund.current_hold_value -= order_cost
            self.fund.latest_buy_price = market_order.price
            self.fund.total_traded_value += order_cost
            #avg cost
            curr_total_crypto_size = (self.crypto.current_hold_size + self.crypto.current_size)
            self.fund.current_avg_buy_price = (((self.fund.current_avg_buy_price *
                                                  curr_total_crypto_size) + (order_cost))/
                                                        (curr_total_crypto_size + market_order.request_size))
            #crypto
            self.crypto.current_size += market_order.filled_size
            self.crypto.latest_traded_size = market_order.filled_size
            self.crypto.total_traded_size += market_order.filled_size
            
    def _buy_order_canceled(self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #Valid order
            order_cost = (market_order.remaining_size*market_order.price)
            self.fund.current_hold_value -= order_cost
            self.fund.current_value += order_cost
            
    def _sell_order_create (self, trade_req):
        if (sims.simulator_on):
            order = sims.sell (trade_req)
        else:
            order = self.exchange.sell (trade_req)
        #update fund 
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #successful order
            log.debug ("SELL Order Sent to exchange. ")      
            return market_order 
        else:
            log.debug ("SELL Order Failed to place")
            return None        

    def _sell_order_received (self, order):
        #log.debug ("SELL RECV: %s"%(json.dumps(order, indent=4, sort_keys=True)))
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #successful order
            #update fund 
            order_type = market_order.order_type
            size = 0
            if order_type == 'market':
                size = Decimal(market_order.request_size) 
            elif order_type == 'limit':
                size = Decimal (market_order.request_size)
            else:
                log.error ("BUY: unknown order_type: %s"%(order_type))
                return
            self.crypto.current_hold_size += size
            self.crypto.current_size -= size            
                        
    def _sell_order_filled (self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #Valid order       
            order_cost = (market_order.filled_size*market_order.price)        
            #fund
            self.fund.current_value += order_cost
            #crypto
            self.crypto.current_hold_size -= (market_order.filled_size + market_order.remaining_size)
            self.crypto.current_size += market_order.remaining_size
            #profit
            profit = (market_order.price - self.fund.current_avg_buy_price )*market_order.filled_size
            self.fund.current_realized_profit += profit
            
    def _sell_order_canceled(self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #Valid order
            self.crypto.current_hold_size -= market_order.remaining_size
            self.crypto.current_size += market_order.remaining_size

    def _save_order (self, trade_req, order):
        db.db_add_or_update_order (self, trade_req.product, order)
        #TODO: FIXME: jork: implement
        
    def _get_manual_trade_req (self):
        exchange_name = self.exchange.__name__
        trade_req_list = []
        manual_file_name = "override/TRADE_%s.%s"%(exchange_name, self.product_id)
        if os.path.isfile(manual_file_name):
            log.info ("Override file exists - "+manual_file_name)
            with open(manual_file_name) as fp:
                trade_req_dict = json.load(fp)
                #delete the file after reading to make sure multiple order from same orderfile
                os.remove(manual_file_name)
                # Validate
                if (trade_req_dict != None and trade_req_dict['product'] == self.product_id ):
                    trade_req = TradeRequest(Product=trade_req_dict['product'],
                                              Side=trade_req_dict['side'],
                                               Size=round(Decimal(trade_req_dict['size']),8),
                                                Type=trade_req_dict['type'],
                                                 Price=round(Decimal(trade_req_dict['price']), 8),
                                                 Stop=trade_req_dict['stop'])
                    log.info("Valid manual order : %s"%(str(trade_req)))
                    trade_req_list.append(trade_req)
        return trade_req_list       
    
    def _generate_trade_request (self, signal):
        '''
        Desc: Consider various parameters and generate a trade request
        Algo: 
        '''
        log.debug ('Calculate trade Req')
            #TODO: jork: implement
        return None

    def _execute_market_trade(self, trade_req_list):
        '''
        Desc: Execute a trade request on the market. 
              This API calls the sell/buy APIs of the corresponding exchanges 
              and expects the order in uniform format
        '''
        for trade_req in trade_req_list:
            log.debug ("Executing Trade Request:"+str(trade_req))
            if (trade_req.type == 'limit'):
                if (trade_req.side == 'BUY'):
                    order = self._buy_order_create (trade_req)
                elif (trade_req.side == 'SELL'):
                    order = self._sell_order_create (trade_req)
                if (order == None):
                    log.error ("Placing Order Failed!")
                    return
                #Add the successful order to the db
                self._save_order (trade_req, order)
            elif (trade_req.type == 'stop'):
                #  Stop order, add to pending list
                log.debug("pending(stop) trade_req %s"%(str(trade_req)))
                self.order_book.add_pending_trade_req(trade_req)
    
    def _import_historic_candles (self):
        ### TODO: FIXME: jork: db implementations for historic data
        # import Historic Data 
        try:
            self.exchange.get_historic_rates
        except NameError:
            log.critical("method 'get_historic_rates()' not defined for exchange!!")
        else:
            log.debug ("Importing Historic rates #num Candles")            
            candle_list = self.exchange.get_historic_rates(self.product_id)
            if candle_list:        
                self.market_indicators_data = []
                for candle in candle_list:
                    self.market_indicators_data.append({'ohlc': candle})
                #log.debug ("Imported Historic rates #num Candles (%s)", str(self.market_indicators))

    def _calculate_historic_indicators (self):
        hist_len  = 0 if not self.market_indicators_data else len(self.market_indicators_data)
        if not hist_len:
            return
        
        log.debug ("re-Calculating all indicators for historic data #candles (%d)"%(hist_len))
        for idx in range (hist_len):
            self._calculate_all_indicators (idx)
                    
    def _calculate_all_indicators (self, candle_idx):
        log.debug ("setting up all indicators for periods indx: %d"%(candle_idx))
        for indicator in self.indicator_calculators:
            start = candle_idx - indicator.period
            period_data = self.market_indicators_data [(0 if start < 0 else start):indicator.period]
            new_ind = indicator.calculate(period_data)
            self.market_indicators_data [candle_idx][indicator.name] = new_ind
            log.debug ("indicator (%s) val (%d)"%(indicator.name, new_ind))
        
        
    ##########################################
    ############## Public APIs ###############    
    def market_setup (self):
        ''' 
        Restore the market states for our work
        WHenver possible, restore from the local db
        1. Get historic rates
        2. Calculate the indicators based on configured strategies 
        '''
        self._import_historic_candles()
        self._calculate_historic_indicators()
        
        
    def update_market_states (self):
        '''
        Desc: 1. Update/refresh the various market states (rate, etc.)
              2. perform any pending trades (stop requests)
              3. Cancel/timeout any open orders if need be
        '''
        #TODO: jork: implement    
        #1.update market states
        if (self.order_book.book_valid == False):
            log.debug ("Re-Construct the Order Book")
            self.order_book.reset_book()     
        #2.pending trades
        self._handle_pending_trades ()
        
    def generate_trade_signal (self):
        """ 
        Do all the magic to generate the trade signal
        params : exchange, product
        return : trade signal (-5..0..5)
                 -5 strong sell
                 +5 strong buy
        """
        #TODO: jork: implement
        
        log.info ("Generate Trade Signal for product: "+self.product_id)
        
        signal = 0 
        
        ################# TODO: FIXME: jork: Implementation ###################
        
        return signal
    
    def consume_trade_signal (self, signal):
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
        exchange_name = self.exchange.__name__
        ignore_file = "override/%s_%s.ignore"%(exchange_name, self.product_id)
        #Override file name = override/TRADE_<exchange_name>.<product>
        if (os.path.isfile(ignore_file)):
            log.info("Ignore file present for product. Skip processing! "+ignore_file)
            return
        #get manual trade reqs if any
        trade_req_list = self._get_manual_trade_req ()
        # Now generate auto trade req list
        log.info ("Trade Signal strength:"+str(signal))         ## TODO: FIXME: IMPLEMENT:
        trade_req = self._generate_trade_request( signal)
        #validate the trade Req
        if (trade_req != None and trade_req.size > 0 and trade_req.price > 0):
            ## Now we have a valid trader request
            # Execute the trade request and retrieve the order # and store it
            trade_req_list.append(trade_req)
        if (len(trade_req_list)):
            self._execute_market_trade(trade_req_list)

    def __str__(self):
        return "{'product_id':%s,'name':%s,'exchange_name':%s,'fund':%s,'crypto':%s,'orders':%s}"%(
                self.product_id,self.name,self.exchange_name, 
                str(self.fund), str(self.crypto), str(self.order_book))
        
        
############# Market Class Def - end ############# 

# Feed Q routines
feedQ = Queue.Queue()
def feed_enQ (market, msg):
    obj = {"market":market, "msg":msg}
    feedQ.put(obj)
    
def feed_deQ (timeout):
    try:
        if (timeout == 0):
            msg = feedQ.get(False)
        else:
            msg = feedQ.get(block=True, timeout=timeout)
    except Queue.Empty:
        return None
    else:
        return msg

def feed_Q_process_msg (msg):
    log.debug ("-------feed msg -------")
    market = msg["market"]
    if (market!= None):
        market.market_consume_feed(msg['msg'])

def get_market_list ():
    return OldMonk_market_list

def get_market_by_product (product_id):
    for market in OldMonk_market_list:
        if market.product_id == product_id:
            return market
        
def market_init (exchange_list):
    '''
    Initialize per exchange, per product data.
    This is where we want to keep all the run stats
    '''
    global OldMonk_market_list
    for exchange in exchange_list:
        for product in exchange.get_products():
            market = exchange.market_init (exchange, product)
            if (market == None):
                log.critical ("Market Init Failed for exchange: %s product: %s"%(exchange.__name__, product['id']))
            else:
                OldMonk_market_list.append(market)
                 
def market_setup ():         
    '''
    Setup market states.
    This is where we want to keep all the run stats
    '''
    global OldMonk_market_list
    for market in OldMonk_market_list:
            status = market.market_setup ()
            if (status == False):
                log.critical ("Market Init Failed for market: %s"%(market.name))
            else:
                log.info ("Market setup completed for market: %s"%(market.name))
#EOF
