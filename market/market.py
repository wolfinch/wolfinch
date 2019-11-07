# OldMonk Auto trading Bot
# Desc: Market/trading routines
# Copyright 2019, Joshith Rayaroth Koderi. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

##############################################
###### Bugs/Caveats, TODOs, AIs###############
### 2. Use Fee and enhance to maker/taker fees


##############################################
import json
import sys
import os
import Queue
# import pprint
from itertools import product
from decimal import Decimal
from datetime import datetime
import time
import random

from utils import *
from order_book import OrderBook
from order import TradeRequest
from decision import Decision
import decision
import db
import sims
import strategy

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

log = getLogger ('MARKET')
log.setLevel(log.INFO)

OldMonk_market_list = []

class OHLC(object): 
    __slots__ = ['time', 'open', 'high', 'low', 'close', 'volume']
    def __init__ (self, time=0, open=0, high=0, low=0, close =0, volume =0):
        self.time = time
        self.open = Decimal(open)
        self.high = Decimal(high)
        self.low  = Decimal(low)
        self.close = Decimal(close)
        self.volume = Decimal(volume)
    def __str__ (self):
        return '{"time": "%s", "open": %g, "high": %g, "low": %g, "close": %g, "volume": %g}'%(
            str(self.time), self.open, self.high, self.low, self.close, self.volume)
    def __repr__ (self):
        return self.__str__()
     
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
        self.fund_max_liquidity = Decimal(0.0)
        self.fund_liquidity_percent = Decimal(0.0)
        self.max_per_buy_fund_value = Decimal(0.0)
        self.maker_fee_rate = 0
        self.taker_fee_rate = 0
        self.fee_accrued = Decimal(0)        
            
    def set_initial_value (self, value):
        self.initial_value = self.current_value = Decimal(value)
        
    def set_fund_liquidity_percent (self, value):
        self.fund_liquidity_percent = Decimal(value)
        
    def set_fund_liquidity (self, value):        
        self.fund_max_liquidity = Decimal(value)
        
    def set_hold_value (self, value):
        self.current_hold_value = Decimal(value)      
        
    def set_max_per_buy_fund_value (self, value):
        self.max_per_buy_fund_value = Decimal(value)
    
    def set_fee(self, maker_fee, taker_fee):
        self.maker_fee_rate = maker_fee
        self.taker_fee_rate = taker_fee          

    def get_fund_to_trade (self, num_order):
#         liquid_fund = self.initial_value *  self.fund_liquidity_percent / Decimal(100)
        rock_bottom = self.initial_value - self.fund_max_liquidity
        
        fund = self.max_per_buy_fund_value * num_order
        log.debug ("fund: %s slice: %s num_order: %s"%(fund, self.max_per_buy_fund_value, num_order))
        
        if self.current_value - (self.current_hold_value + fund) < rock_bottom:
            log.error ("**** No Funds to trade. num_order(%d) ****"%(num_order))
            return 0
        else:
            #  hold fund 
            self.current_hold_value += fund
            return fund
    def buy_confirm (self, num_order, fund, fees):
        #release hold and account actual cost
        self.current_hold_value -= (self.max_per_buy_fund_value * num_order)
        self.current_value -= fund
        self.total_traded_value += fund
        self.fee_accrued += fees  
                
    def sell_confirm (self, fund, fees):
        self.current_value += fund
        self.total_traded_value += fund
        self.fee_accrued += fees
        
    def trade_fail (self, num_order):
        #release the hold
        self.current_hold_value -= (self.max_per_buy_fund_value * num_order)
        
        
    def __str__(self):
        return ("""
{
"initial_value":%f,"current_value":%f,"current_hold_value":%f, "total_traded_value":%f, "fee_accrued": %f,
"current_realized_profit":%f,"current_unrealized_profit":%f, "total_profit":%f,
"current_avg_buy_price":%f,"latest_buy_price":%f,
"fund_liquidity_percent":%d, "max_per_buy_fund_value":%d
}""")%(
            self.initial_value, self.current_value, self.current_hold_value,
             self.total_traded_value, self.fee_accrued, self.current_realized_profit, 
             self.current_unrealized_profit, self.total_profit, self.current_avg_buy_price, 
             self.latest_buy_price, self.fund_liquidity_percent, self.max_per_buy_fund_value )
                
class Asset:
    def __init__(self):    
        self.initial_size = Decimal(0.0)
        self.current_size = Decimal(0.0)
        self.latest_traded_size = Decimal(0.0)
        self.current_hold_size = Decimal(0.0)
        self.total_traded_size = Decimal(0.0)
        self.max_per_trade_size = Decimal(0.0)
        self.min_per_trade_size = Decimal(0.0)
        self.hold_size = Decimal(0.0)
    
    def set_max_per_trade_size (self, size):
        self.max_per_trade_size = size
        
    def set_min_per_trade_size (self, size):
        self.min_per_trade_size = Decimal(size)        
            
    def set_initial_size (self, size):
        self.initial_size = self.current_size = size
    
    def get_initial_size (self):
        return self.initial_size
    
    def get_current_size (self):
        return self.current_size
        
    def set_hold_size (self, size):
        self.hold_size = Decimal(size)
        
    def get_asset_to_trade (self, size):        
#         cur_size = self.max_per_trade_size * strength
#         if ((self.current_size - self.current_hold_size) >= (cur_size + self.hold_size)):
        if ((self.current_size - self.current_hold_size) >= size):
            self.current_hold_size += size
            return size
        else:
            log.error("**** No Assets to trade. size(%f) ****"%(size))
            return 0
    def buy_confirm (self, size):
        self.current_size += size
        self.latest_traded_size = size
        self.total_traded_size += size
    def sell_confirm (self, size):
        self.current_size -= size
        self.current_hold_size -= size
        self.latest_traded_size = size
        self.total_traded_size += size
    def trade_fail (self, size):
        self.current_hold_size -= size
    def __str__(self):
        return ("""{
"initial_size":%f, "current_size":%f, "hold_size": %f, "current_hold_size":%f, 
"max_per_trade_size":%f, "min_per_trade_size":%f, "latest_traded_size":%f, "total_traded_size":%f
}""")%(
            Decimal(self.initial_size), Decimal(self.current_size), Decimal(self.hold_size), Decimal(self.current_hold_size),
            Decimal(self.max_per_trade_size), Decimal(self.min_per_trade_size),
             Decimal(self.latest_traded_size), Decimal(self.total_traded_size))
                
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
#      asset {
#      initial_size:
#      current_size:
#      current_hold_size:
#      current_avg_value:
#      total_traded_size:
#      }
#      orders {
#      total_order_num
#      pending_buy_orders_db: <dict>
#      pending_sell_orders_db: <dict>
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
        #init states:
        self.primary = True
        self.num_buy_req =0 
        self.num_sell_req = 0
        self.num_buy_req_reject = 0
        self.num_sell_req_reject = 0
        self.num_buy_order = 0
        self.num_sell_order = 0    
        self.num_buy_order_success = 0
        self.num_sell_order_success = 0    
        self.num_buy_order_failed = 0
        self.num_sell_order_failed = 0
        self.num_take_profit_hit = 0
        self.num_stop_loss_hit = 0
        self.num_success_trade = 0
        self.num_failed_trade = 0
        
        #config
        self.product_id = None if product == None else product['id']
        self.name = None if product == None else product['display_name']
        self.fund_type = product['fund_type']
        self.asset_type = product['asset_type']
        self.exchange_name = None if exchange == None else exchange.name
        self.exchange = exchange       #exchange module
        
        #set primary?
        self.primary = exchange.primary
        
        self.current_market_rate = Decimal(0.0)
        self.start_market_rate = Decimal(0.0)
        self.consume_feed = None
        self.fund = Fund ()
        self.asset = Asset ()
        self.order_book = OrderBook(market=self)
        
        tcfg, dcfg = exchange.get_product_config (self.exchange_name, self.product_id)
        if tcfg == None or dcfg == None:
            log.critical ("Unable to get product config for exch: %s prod: %s"%(self.exchange_name, self.product_id))
            raise Exception ("Unable to get product config for exch: %s prod: %s"%(self.exchange_name, self.product_id))
        else:
            log.info ("tcfg: %s dcfg: %s"%(tcfg, dcfg))
            
        self.tradeConfig = tcfg
        self.decisionConfig = dcfg  
        decision.decision_config (self.exchange_name, self.product_id, self.decisionConfig['model_type'], self.decisionConfig['model_config'])    
        self.decision = None  #will setup later
        
        #initialize params
        self.fund.set_initial_value(Decimal(0.0))
        self.fund.set_hold_value(Decimal(0.0))
        self.fund.set_fund_liquidity(tcfg['fund_max_liquidity'])
        self.fund.set_max_per_buy_fund_value(tcfg['fund_max_per_buy_value'])
        fee = tcfg.get('fee')
        if fee:
            self.fund.set_fee(fee['maker'], fee['taker'])
        self.asset.set_initial_size(Decimal(0.0))
        self.asset.set_hold_size( Decimal(0.0))
        self.asset.set_max_per_trade_size(tcfg['asset_max_per_trade_size'])
        self.asset.set_min_per_trade_size(tcfg['asset_min_per_trade_size'])        
            
        #order type
        self.order_type = tcfg.get('order_type', "market")
        
        # Market Strategy related Data
        # [{'ohlc':(time, open, high, low, close, volume), 'sma':val, 'ema': val, name:val...}]
        self.market_indicators_data     = []
        self.market_strategies_data     = []
        self.cur_candle_time = 0
        self.cur_candle_vol = 0
        self.num_candles        = 0
        self.candlesDb = db.CandlesDb (OHLC, self.exchange_name, self.product_id)

        strategy_list = decision.get_strategy_list(self.exchange_name, self.product_id)
        if strategy_list == None:
            log.critical ("invalid strategy_list!!")
            raise ("invalid strategy_list")
        self.market_strategies     = strategy.Configure(self.exchange_name, self.product_id, strategy_list)
        self.indicator_calculators = strategy.Configure_indicators(self.exchange_name, self.product_id)        
        self.new_candle = False
        self.candle_interval = 0
        self.O = self.H = self.L = self.C = self.V = 0
        
        self._pending_order_track_time = 0
        self._db_commit_time = 0
            
    def __str__(self):
#         log.critical ("get_market_rate:%f start_market_rate:%f initial_value:%f fund_liquidity_percent:%f start_market_rate:%f"%(
#             self.get_market_rate(), self.start_market_rate,
#                     self.fund.initial_value, self.fund.fund_liquidity_percent, self.start_market_rate))
        return """
{
"exchange_name": "%s", "product_id": "%s","name": "%s", "current_market_rate": %f,
"cur_candle_time": %d, "cur_candle_vol": %f, "num_candles": %d,
"num_buy_req": %s, "num_buy_req_reject": %s,
"num_sell_req": %s, "num_sell_req_reject": %s,
"num_buy_order": %s, "num_buy_order_success": %s, "num_buy_order_failed": %s,                   
"num_sell_order": %s, "num_sell_order_success": %s, "num_sell_order_failed": %s,
"num_take_profit_hit": %d, "num_stop_loss_hit": %d,
"num_success_trade": %d, "num_failed_trade": %d,
"cur_buy_and_hold_profit": %f,
"fund":%s,
"asset":%s,
"order_book":%s
}"""%(
                self.exchange_name, self.product_id, self.name, round(self.current_market_rate, 4),
                self.cur_candle_time, self.cur_candle_vol, self.num_candles, 
                self.num_buy_req, self.num_buy_req_reject,
                self.num_sell_req, self.num_sell_req_reject,
                self.num_buy_order, self.num_buy_order_success, self.num_buy_order_failed, 
                self.num_sell_order, self.num_sell_order_success, self.num_sell_order_failed,
                self.num_take_profit_hit, self.num_stop_loss_hit,
                self.num_success_trade, self.num_failed_trade,
                (self.get_market_rate() - self.start_market_rate)*(
                    self.fund.initial_value*Decimal(0.01)*self.fund.fund_liquidity_percent/self.start_market_rate),
                str(self.fund), str(self.asset), str(self.order_book))        
        
    def set_candle_interval (self, value):
        self.candle_interval = value        
        
    def get_candle_list (self):
        return map(lambda x: x["ohlc"], self.market_indicators_data)
    
    def get_indicator_list (self):
        return self.market_indicators_data    
    
    def get_strategies_list (self):
        return self.market_strategies_data        
    
    def set_market_rate (self, price):
        self.current_market_rate = price
        
    def get_market_rate (self):
        if sims.backtesting_on == True:
            return self.market_indicators_data[self.backtesting_idx]['ohlc'].close
        else:        
            return self.current_market_rate       
        
    def register_feed_processor (self, feed_processor_cb):
        self.consume_feed = feed_processor_cb
        
    def market_consume_feed(self, msg):
        if (self.consume_feed != None):
            self.consume_feed(self, msg)
            
    def tick(self, price, l_size):
        if (price == 0 or not l_size):
            log.error ("Invalid price or 'last_size' in ticker feed")
            return
        size = Decimal(l_size)
        
        #update ticker
        if self.O == 0:
            self.O = self.H = self.L = price
        else:
            if price < self.L:
                self.L = price
            if price > self.H:
                self.H = price
#         v += size
        self.V += size
        
        now = time.time()
#         log.critical("next_cdl: %d now: %d"%(market.cur_candle_time+self.candle_interval, now))
        if now >= self.cur_candle_time + self.candle_interval:
            # close the current candle period and start a new candle period
            c = price
            candle = OHLC(long(now), self.O, self.H, self.L, c, self.V)
            log.debug ("New candle identified %s"%(candle))        
            self.add_new_candle (candle)
            
            
        #TODO: FIXME: jork: might need to rate-limit the logic here after
        self.set_market_rate (price)

    def _handle_take_profit (self):
 
        trade_pos_l = self.order_book.get_take_profit_positions(self.get_market_rate())
                
        #validate the trade Req
        num_pos = len(trade_pos_l)
        if (num_pos):
            trade_req_l = []
            log.info ("(%d) pos hit take profit"%(num_pos)) 
            for pos in trade_pos_l:
                asset_size = pos.buy.get_asset()
                if (asset_size <= 0):
                    log.critical ("Invalid open position for closing: pos: %s"%str(pos))
                    raise Exception("Invalid open position for closing")
                log.debug ("Generating take profit SELL trade_req with asset size: %s"%(str(asset_size)))   
                trade_req_l.append(TradeRequest(Product=self.product_id,
                                  Side="SELL",
                                   Size=round(Decimal(asset_size),8),
                                   Fund=round(Decimal(0), 8),                                   
                                   Type="market",
                                   Price=round(Decimal(0), 8),
                                   Stop=0, id=pos.id))            
            
            self._execute_market_trade(trade_req_l)
                
    def _handle_pending_trade_reqs (self):
        #TODO: FIXME:jork: Might need to extend

        num_pos = len(self.order_book.pending_trade_req)
        if 0 == num_pos:
            return 
        log.debug("(%d) Pending Trade Reqs "%(num_pos))        
        
        market_price = self.get_market_rate()
        for trade_req in self.order_book.pending_trade_req[:]:
            if (trade_req.side == 'BUY'):
                if (trade_req.stop >= market_price):
                    self.buy_order_create(trade_req)
                    self.order_book.remove_pending_trade_req(trade_req)
                else:
                    log.debug("STOP BUY: market(%g) higher than STOP (%g)"%(self.get_market_rate(), trade_req.stop))
            elif (trade_req.side <= 'SELL'):
                if (trade_req.stop <= market_price):
                    self.sell_order_create(trade_req)
                    self.order_book.remove_pending_trade_req(trade_req)     
                else:
                    log.debug("STOP SELL: market(%g) lower than STOP (%g)"%(self.get_market_rate(), trade_req.stop))                                   
    
    def order_status_update (self, order):
        log.debug ("ORDER UPDATE: %s"%(str(order)))
        
        ### TODO: if order pending for too long (cfg), cancel order
        
        if order == None:
            log.error ("Invalid order, skip update")
            return None
        
        side = order.side
        msg_type = order.status_type
        reason = order.status_reason
        if side == 'buy':
            if msg_type == 'done':
                #for an order done, get the order details             
                if (sims.simulator_on):
                    order_det = sims.exch_obj.get_order(order.id)
                    if (order_det):
                        order = order_det                    
                else:                
                    order_det = self.exchange.get_order(order.id)
                    if (order_det):
                        order = order_det
                    else:
                        # Unknown error here. We should keep trying for the pending order tracking.
                        log.critical ("unable to get order details for done order(%s)"%(order.id))
                        return None
                if reason == 'filled':
                    self._buy_order_filled ( order)                    
                elif reason == 'canceled':
                    self._buy_order_canceled (order)
                else:
                    log.error ("unknown order done reason(%s)"%(reason))                    
            elif msg_type == 'received':
                self._buy_order_received(order)
            elif (msg_type in ['open', 'match', 'change', 'margin_profile_update', 'activate' ]):
                log.debug ("Ignored buy order status: %s"%(msg_type))
            else:
                log.critical ("Unknown buy order status: %s"%(msg_type))
                raise Exception("Unknown buy order status: %s"%(msg_type))
        elif side == 'sell':
            if msg_type == 'done':
                #for an order done, get the order details              
                if (sims.simulator_on):
                    order_det = sims.exch_obj.get_order(order.id)
                    if (order_det):
                        order = order_det                    
                else:                
                    order_det = self.exchange.get_order(order.id)
                    if (order_det):
                        order = order_det
                    else:
                        # Unknown error here. We should keep trying for the pending order tracking.
                        log.critical ("unable to get order details for done order(%s)"%(order.id))
                        return None               
                if reason == 'filled':
                    self._sell_order_filled ( order)
                elif reason == 'canceled':
                    self._sell_order_canceled (order)
                else:
                    log.error ("unknown order done reason(%s)"%(reason))
            elif msg_type == 'received':
                self._sell_order_received(order)
            elif (msg_type in ['open', 'match', 'change', 'margin_profile_update', 'activate']):
                log.debug ("Ignored sell order status: %s"%(msg_type))
            else:
                log.error ("Unknown sell order status: %s"%(msg_type))
                raise Exception("Unknown sell order status: %s"%(msg_type))                
        else:
            log.error ("Unknown order Side (%s)"%(side))
            raise Exception("Unknown order Side (%s)"%(side))
                    
    def _buy_order_received (self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #successful order
            log.info ("BUY RECV>>> request_size:%s funds:%s"%(
                round(market_order.request_size, 4), round(market_order.funds, 4)))
            
#             #update fund 
#             order_type = market_order.order_type
#             order_cost = 0
#             if order_type == 'market':
#                 order_cost = Decimal(market_order.funds) 
#             elif order_type == 'limit':
#                 order_cost = Decimal (market_order.price) * Decimal (market_order.request_size)
#             else:
#                 log.error ("BUY: unknown order_type: %s"%(order_type))
#                 return
#             
#             if order_cost == 0:
#                 log.critical ("Invalid order_cost!")
#                 raise Exception("Invalid order_cost!")
#             self.fund.current_hold_value += order_cost
#             self.fund.current_value -= order_cost
        else:
            log.critical("Invalid Market_order filled order:%s"%(str(order)))
            raise Exception("Invalid Market_order filled order:%s"%(str(order)))            
                                        
    def _buy_order_create (self, trade_req):
        
        self.num_buy_order += 1
        log.info("BUY: %d sig: %s"%(self.num_buy_order, trade_req))
        if (sims.simulator_on):
            order = sims.exch_obj.buy (trade_req)
        else:
            order = self.exchange.buy (trade_req)
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #successful order
            log.debug ("BUY Order Sent to exchange. ")
            return market_order
        else:
            log.debug ("BUY Order Failed to place")
            self.fund.trade_fail(1)
            self.num_buy_order_failed += 1            
            return None
            
    def _buy_order_filled (self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #Valid order
            log.info ("BUY FILLED>>> filled_size:%s price:%s"%(
                round(market_order.filled_size, 4), round(market_order.price, 4)))
            order_cost = (market_order.filled_size*market_order.price) + market_order.fees
            #fund
            self.fund.buy_confirm(1, order_cost, market_order.fees)
            
#             self.fund.current_hold_value -= order_cost
#             self.fund.total_traded_value += order_cost
#             self.fund.fee_accrued += market_order.fees      
                  
            #avg cost
            curr_new_asset_size = (self.asset.current_hold_size + self.asset.current_size - self.asset.initial_size)
            self.fund.latest_buy_price = market_order.price            
            self.fund.current_avg_buy_price = (((self.fund.current_avg_buy_price *
                                                  curr_new_asset_size) + (order_cost))/
                                                        (curr_new_asset_size + market_order.filled_size))
            #asset
            self.asset.buy_confirm(market_order.filled_size)
            
            #stats
            self.num_buy_order_success += 1            
        else:
            log.critical("Invalid Market_order filled order:%s"%(str(order)))
            raise Exception("Invalid Market_order filled order:%s"%(str(order)))            
            
    def _buy_order_canceled(self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #Valid order
            self.fund.trade_fail(1)
#             order_cost = (market_order.remaining_size*market_order.price)
#             self.fund.current_hold_value -= order_cost
#             self.fund.current_value += order_cost
    
    def _sell_order_create (self, trade_req):
        self.num_sell_order += 1
        log.info("SELL: %d sig: %s"%(self.num_sell_order, trade_req))
        if (sims.simulator_on):
            order = sims.exch_obj.sell (trade_req)
        else:
            order = self.exchange.sell (trade_req)
        #update fund 
        order._pos_id = trade_req.id
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #successful order
            log.debug ("SELL Order Sent to exchange. ")      
            return market_order 
        else:
            self.asset.trade_fail (trade_req.size)
            self.num_sell_order_failed += 1                        
            log.debug ("SELL Order Failed to place")
            return None        

    def _sell_order_received (self, order):
#         log.critical ("SELL RECV: %s"%(json.dumps(order, indent=4, sort_keys=True)))
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #successful order
            log.info ("SELL RECV>>> request_size:%s price:%s"%(
                round(market_order.request_size, 4), round(market_order.price, 4)))            
#             #update fund 
#             order_type = market_order.order_type
#             size = 0
#             if order_type == 'market':
#                 size = Decimal(market_order.request_size) 
#             elif order_type == 'limit':
#                 size = Decimal (market_order.request_size)
#             else:
#                 log.error ("SELL: unknown order_type: %s"%(order_type))
#                 return
#             self.asset.current_hold_size += size
#             self.asset.current_size -= size
        else:
            log.critical("Invalid Market_order filled order:%s"%(str(order)))
            raise Exception("Invalid Market_order filled order:%s"%(str(order)))
                        
    def _sell_order_filled (self, order):
        # TODO: FIXME: FIX real order cost. it may be less fee
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #Valid order
            order_cost = (market_order.filled_size*market_order.price)        
            #fund
            self.fund.sell_confirm(order_cost, market_order.fees)
#             self.fund.current_value += order_cost
#             self.fund.fee_accrued += market_order.fees
            #asset
            self.asset.sell_confirm(market_order.filled_size)
#             self.asset.current_hold_size -= (market_order.filled_size + market_order.remaining_size)
#             self.asset.current_size += market_order.remaining_size
#             self.asset.latest_traded_size = market_order.filled_size
#             self.asset.total_traded_size += market_order.filled_size            
            #profit
            # NOTE: move the profit calculation to position close, that's more accurate
#             profit = (market_order.price - self.fund.current_avg_buy_price )*market_order.filled_size
#             self.fund.current_realized_profit += profit
            #stats
            self.num_sell_order_success += 1
            log.info ("SELL FILLED>>> filled_size:%s price:%s "%(
                round(market_order.filled_size, 4), round(market_order.price, 4)))            
        else:
            log.critical("Invalid Market_order filled order:%s"%(str(order)))
            raise Exception("Invalid Market_order filled order:%s"%(str(order)))
            
    def _sell_order_canceled(self, order):
        market_order  =  self.order_book.add_or_update_my_order(order)
        if(market_order): #Valid order
            self.asset.trade_fail(market_order.remaining_size)
#             self.asset.current_hold_size -= market_order.remaining_size
#             self.asset.current_size += market_order.remaining_size
        
    def _get_manual_trade_req (self):
        exchange_name = self.exchange.name
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
                                               Fund=round(Decimal(0), 8), #TODO: FIXME: make sure correct fund/size                        
                                                Type=trade_req_dict['type'],
                                                 Price=round(Decimal(trade_req_dict['price']), 8),
                                                 Stop=trade_req_dict['stop'])
                    log.info("Valid manual order : %s"%(str(trade_req)))
                    trade_req_list.append(trade_req)
        return trade_req_list       
    
    def _generate_trade_request (self, signal):
        '''
        Desc: Consider various parameters and generate a trade request
        param : Trade signal (-3-0-3) (strong-sell - hold - strong-buy)
        return: Trade request
        Algo: 1. Trade signal 
        '''
        #TODO: FIXME: jork: impl. limit, stop etc
        log.debug ('Calculate trade Req')
        
        trade_req_l = []
        trade_pos_l = []
        #1. if stop loss enabled, get stop loss hit positions
        if self.tradeConfig["stop_loss_enabled"]:
            log.debug ("find pos hit stop loss")
            trade_pos_l += self.order_book.get_stop_loss_positions(self.get_market_rate())
        
        #2. if take profit enabled, get TP hit positions
        if self.tradeConfig["take_profit_enabled"]:
            log.debug ("find pos hit take profit")
            trade_pos_l += self.order_book.get_take_profit_positions(self.get_market_rate())
        
        for pos in trade_pos_l:
            asset_size = pos.buy.get_asset()
            if (asset_size <= 0):
                log.critical ("Invalid open position for closing: pos: %s"%str(pos))
                raise Exception("Invalid open position for closing")
            self.asset.get_asset_to_trade(asset_size)
            log.debug ("Generating watermark SELL trade_req with asset size: %s"%(str(asset_size)))   
            trade_req_l.append(TradeRequest(Product=self.product_id,
                              Side="SELL",
                               Size=round(Decimal(asset_size),8),
                               Fund=round(Decimal(0), 8),                                   
                               Type=self.order_type,
                               Price=round(Decimal(0), 8),
                               Stop=0, id=pos.id))
        
        #3. do regular trade req based on signal
        abs_sig = abs(signal)  
        while (abs_sig):  
            abs_sig -= 1
            if signal > 0 :
                #BUY
                self.num_buy_req += 1
                fund = self.fund.get_fund_to_trade(1)
                if fund > 0:
                    size = fund / self.get_market_rate()
                    #normalize size
                    size_norm = round(Decimal((size - size % self.asset.min_per_trade_size)), 8)
                    if size_norm == 0 :
                        log.critical ("buy size too small min_size: %f size: %f", self.asset.min_per_trade_size, size)
                        continue
                    log.debug ("Generating BUY trade_req with fund: %d size: %d for signal: %d"%(fund, size_norm, signal))
                    trade_req_l.append(TradeRequest(Product=self.product_id,
                                      Side="BUY",
                                       Size=size_norm,
                                       Fund=round(Decimal(fund), 8),
                                       Type="market",
                                       Price=round(Decimal(0), 8),
                                       Stop=0))
                else:
                    log.debug ("Unable to generate BUY request for signal (%d). Too low fund"%(signal))
                    self.num_buy_req_reject += 1                
#                     return trade_req_l
            elif signal < 0:
                # SELL
                self.num_sell_req += 1                            
#                 asset_size = self.asset.get_asset_to_trade (1)
                position = self.order_book.get_closable_position()
                if position:
#                     log.debug ("pos: %s"%(str(position)))
                    asset_size = position.buy.get_asset()
                    if (asset_size <= 0):
                        log.critical ("Invalid open position for closing: pos: %s"%str(position))
                        raise Exception("Invalid open position for closing")
                    self.asset.get_asset_to_trade(asset_size)
                    log.debug ("Generating SELL trade_req with asset size: %s"%(str(asset_size)))       
                    trade_req_l.append(TradeRequest(Product=self.product_id,
                                      Side="SELL",
                                       Size=round(Decimal(asset_size),8),
                                       Fund=round(Decimal(0), 8),                                   
                                       Type="market",
                                       Price=round(Decimal(0), 8),
                                       Stop=0, id=position.id))
                else:
                    log.error ("Unable to generate SELL request for signal (%d)."
                     "Unable to get open positions to sell"%(signal))
                    self.num_sell_req_reject += 1                                
#                     return trade_req_l
            else:
                #signal 0 - hold signal
                return trade_req_l
        return trade_req_l

    def _execute_market_trade(self, trade_req_list):
        '''
        Desc: Execute a trade request on the market. 
              This API calls the sell/buy APIs of the corresponding exchanges 
              and expects the order in uniform format
        '''
        for trade_req in trade_req_list:
            log.debug ("Executing Trade Request:"+str(trade_req))
            if (trade_req.type == 'limit' or trade_req.type == 'market'):
                if (trade_req.side == 'BUY'):
                    order = self._buy_order_create (trade_req)
                elif (trade_req.side == 'SELL'):
                    order = self._sell_order_create (trade_req)
                if (order == None):
                    log.error ("Placing Order Failed!")
                    return
            elif (trade_req.type == 'stop'):
                #  Stop order, add to pending list
                log.debug("pending(stop) trade_req %s"%(str(trade_req)))
                self.order_book.add_pending_trade_req(trade_req)
        
    def _normalize_candle_list_helper (self, cdl_list_db, cdl_list_exch):
        # we can optimize this based on list order
        if (cdl_list_db == None or (len(cdl_list_db) <= 0)):
            return cdl_list_exch
        i = 0
        for cdl_exch in cdl_list_exch:
            if cdl_exch.time >= cdl_list_db[-1].time:
                break
            i += 1            
        log.info ("new normalized len: %d"%(len(cdl_list_exch) - i))
        return cdl_list_exch[i:]
        
    def _import_historic_candles (self, local_only=False):
#         self.market_indicators_data = []

        log.debug ("%f : db_import before"%(time.time()))
        db_candle_list = self.candlesDb.db_get_all_candles()
        log.debug ("%f : db_import after"%(time.time()))
        
        if db_candle_list:        
            for candle in db_candle_list:
                self.market_indicators_data.append({'ohlc': candle})
                self.market_strategies_data.append({})
                #log.debug('ohlc: %s'%(candle))
                log.debug ("retrieving candle:%s "%str(candle))
        log.critical ("Imported Historic rates #num Candles (%s)", len(self.market_indicators_data))
        
        if local_only:
            log.info ("import local only, skipping history import from exchange.")
            return
        
        # import Historic Data from exchange
        try:
            self.exchange.get_historic_rates
        except NameError:
            log.critical("method 'get_historic_rates()' not defined for exchange!!")
        else:
            start = db_candle_list[-1].time if (db_candle_list and db_candle_list[-1]) else 0            
            log.debug ("Importing Historic rates #num Candles from exchange starting from time: %s to now"%(start))
            candle_list = self.exchange.get_historic_rates(self.product_id, start=(datetime.fromtimestamp(start)
                                                                                     if start > 0 else 0))
#             candle_list = [OHLC(time=10, open=10, high=20, low=10, close=3, volume=3)]
            if candle_list:
                log.debug ("%d candles found from exch"%len(candle_list))
                norm_candle_list = self._normalize_candle_list_helper (db_candle_list, candle_list)
                
                #remove the last entry from db (as the last cdl could be incorrect candle)
                if (len(self.market_indicators_data) > 0):
                    self.market_indicators_data.remove(self.market_indicators_data[-1])
                for candle in norm_candle_list:
                    self.market_indicators_data.append({'ohlc': candle})
                    self.market_strategies_data.append({})
                    log.debug('ohlc: %s'%str(candle))
                #log.debug ("Imported Historic rates #num Candles (%s)", str(self.market_indicators_data))
                #save candles in Db for future
                self.candlesDb.db_save_candles(norm_candle_list)
                log.debug ("imported %d candles from exchange and saved to db"%len(norm_candle_list))                

    def _calculate_historic_indicators (self):
        hist_len  = 0 if not self.market_indicators_data else len(self.market_indicators_data)
        if not hist_len:
            return
        
        log.debug ("re-Calculating all indicators for historic data #candles (%d)"%(hist_len))
        log.info ("#indicators(%d) ind_list:%s"%(len(self.indicator_calculators), str(self.indicator_calculators)))        
        for idx in range (hist_len):
            self._calculate_all_indicators (idx)
        log.debug ("re-Calculated all indicators for historic data #candles (%d)"%(hist_len))            
                    
    def _calculate_all_indicators (self, candle_idx):
#         log.debug ("setting up all indicators for periods indx: %d"%(candle_idx))
        for indicator in self.indicator_calculators:
            start = candle_idx+1 - (indicator.period + 50) #TBD: give few more candles(for ta-lib)
            period_data = self.market_indicators_data [(0 if start < 0 else start):candle_idx+1]
            new_ind = indicator.calculate(period_data)
            self.market_indicators_data [candle_idx][indicator.name] = new_ind
#             log.debug ("indicator (%s) val (%s)"%(indicator.name, str(new_ind)))
        
    def _process_historic_strategies(self):
        hist_len  = 0 if not self.market_indicators_data else len(self.market_indicators_data)
        if not hist_len:
            return
        
        log.debug ("re-proessing all strategies for historic data #candles (%d)"%(hist_len))
        log.info ("#strategies(%d) strat_list:%s"%(len(self.market_strategies), str(self.market_strategies)))
        for idx in range (hist_len):
            self._process_all_strategies (idx)
        log.debug ("re-proessed all strategies for historic data #candles (%d)"%(hist_len))            
                    
    def _process_all_strategies (self, candle_idx):
#         log.debug ("Processing all strategies for periods indx: %d"%(candle_idx))
        for strategy in self.market_strategies:
            start = candle_idx+1 - (strategy.period + 50) #TBD: give few more candles(for ta-lib)
            period_data = self.market_indicators_data [(0 if start < 0 else start):candle_idx+1]
            new_result = strategy.generate_signal(period_data)
            self.market_strategies_data [candle_idx][strategy.name] = new_result
            if new_result != 0: #signal generated
                log.debug ("strategy (%s) val (%s)"%(strategy.name, str(new_result)))
        
    def _init_states(self):
        #calc init avg price
        # We calculate the avg buy price based on the current asset size and first available candle size
        # This may not be the actual avg buy price. 
        # But from our life-cycle perspective, this is good ( or the best we can do.)
        #TODO: Validate: This??
#         self.fund.current_avg_buy_price = 0 #self.get_indicator_list()[0]['ohlc'].close
        log.debug ("_init_states: current_avg_buy_price: %d"%(self.fund.current_avg_buy_price))
        
    ##########################################
    ############## Public APIs ###############
    def market_setup (self, restart=False):
        ''' 
        Restore the market states for our work
        WHenver possible, restore from the local db
        1. Get historic rates
        2. Calculate the indicators based on configured strategies 
        '''
        log.debug ("market (%s) setup"%(self.name))
        
        # do not import candles from exch while backtesting.
        self._import_historic_candles(local_only=sims.backtesting_on)
        
        log.critical ("import complete")
        
        if sims.import_only:
            log.info ("Import only")
            return
        
        # restore market states
        if restart:
            log.info ("restoring order book from DB")
            self._restore_states ()
        
        log.info ("calculating historic indicators")
        log.critical ("%f : _calculate_historic_indicators before "%(time.time()))
        
        self._calculate_historic_indicators()
        log.critical ("%f : _calculate_historic_indicators after "%(time.time()))
        
        log.critical ("calculating historic strategies")
        self._process_historic_strategies()
        log.critical ("%f : _process_historic_strategies aafter "%(time.time()))
        
        num_candles = len(self.market_indicators_data)
        self.cur_candle_time = long(time.time()) if num_candles == 0 else self.market_indicators_data[-1]['ohlc'].time
        if sims.backtesting_on:
            self.start_market_rate = Decimal(0) if num_candles == 0 else self.market_indicators_data[0]['ohlc'].close
        else:
            self.start_market_rate = Decimal(0) if num_candles == 0 else self.market_indicators_data[-1]['ohlc'].close
        self.num_candles = num_candles
        self._init_states()
        log.debug ("market (%s) setup done! num_candles(%d) cur_candle_time(%d)"%(
            self.name, num_candles, self.cur_candle_time))
        log.info ("done setting up historic states")
    
    def _restore_states(self):
        log.info ("restoring market states")
        self.load_market_from_stats()
        
        log.info ("restoring order_book")
        self.order_book.restore_order_book()            
                        
    def load_market_from_stats (self):
        mstats = None
        try:
            with open(MARKET_STATS_FILE%(self.exchange_name, self.product_id), "r") as fd:
                mstats = json.load(fd)
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            log.error ("unable to open file to restore %s:%s"%(self.exchange_name, self.product_id))
            return            
        
        log.info ("loading market stats")
        #restore the stats selectively.
        self.num_buy_req, self.num_buy_req_reject = mstats['num_buy_req'], mstats['num_buy_req_reject']
        self.num_sell_req, self.num_sell_req_reject = mstats['num_sell_req'], mstats['num_sell_req_reject']
        self.num_buy_order, self.num_buy_order_success, self.num_buy_order_failed = \
                                mstats['num_buy_order'], mstats['num_buy_order_success'], mstats['num_buy_order_failed']
        self.num_sell_order, self.num_sell_order_success, self.num_sell_order_failed = \
                                mstats['num_sell_order'], mstats['num_sell_order_success'], mstats['num_sell_order_failed']
        self.num_take_profit_hit, self.num_stop_loss_hit = mstats['num_take_profit_hit'], mstats['num_stop_loss_hit']
        self.num_success_trade, self.num_failed_trade = mstats['num_success_trade'], mstats['num_failed_trade']
        
        #restore fund states
        log.info ("loading fund stats")        
        mf = self.fund
        sf = mstats['fund']
        mf.initial_value = Decimal(sf['initial_value'])
        mf.current_hold_value = Decimal(sf['current_hold_value'])
        mf.total_traded_value = Decimal(sf['total_traded_value'])
        mf.fee_accrued = Decimal(sf['fee_accrued'])
        mf.current_realized_profit = Decimal(sf['current_realized_profit'])
        mf.current_unrealized_profit = Decimal(sf['current_unrealized_profit'])
        mf.total_profit = Decimal(sf['total_profit'])
        mf.current_avg_buy_price = Decimal(sf['current_avg_buy_price'])
        mf.latest_buy_price = Decimal(sf['latest_buy_price'])
        
        #restore asset
        log.info ("loading asset stats")
        ma = self.asset
        sa = mstats['asset'] 
        ma.initial_size = Decimal(sa['initial_size'])
        ma.hold_size = Decimal(sa['hold_size'])
        ma.current_hold_size = Decimal(sa['current_hold_size'])
        ma.latest_traded_size = Decimal(sa['latest_traded_size'])
        ma.total_traded_size = Decimal(sa['total_traded_size'])
        
        
    def _clear_states (self):
        log.info ("clearing market states")
        self.order_book.clear_order_book()
        
    def decision_setup (self, market_list):
        log.debug ("decision setup for market (%s)"%(self.name))
        self.decision = Decision(self, market_list, self.decisionConfig['model_type'], self.decisionConfig['model_config'])
        if self.decision == None:
            log.error ("Failed to setup decision engine")
            return False
        else:
            log.info ("done setup decision engine")
            return True
        
    def lazy_commit_market_states(self):
        now = time.time()
        if self._db_commit_time > now:
            return
        else:
            #setup next commit time, some time between 3min to 5min
            self._db_commit_time = int(now) + random.randrange(180, 300)            
        
        log.debug ("commit positions to db")
        self.order_book.db_commit_dirty_positions()
        

        
    def watch_pending_orders(self):
        now = time.time()
        if self._pending_order_track_time > now:
            return 
        else:
            #setup next commit time, some time between 3min to 5min
            self._pending_order_track_time = int(now) + random.randrange(120, 200)            
        
        log.debug ("watching pending orders")
        pending_order_list = self.order_book.get_all_pending_orders()
        pending_num = len(pending_order_list)
        if not pending_num:
            return
        else:
            log.debug ("(%d) pending orders to watch"%(pending_num))
        for order in pending_order_list:
            if not (sims.simulator_on):
                log.info ("watching pending order(%s)"%(order.id))                
                order_det = self.exchange.get_order(order.id)
                if (order_det):
                    self.order_status_update(order_det)
                else:
                    # Unknown error here. We should keep trying for the pending order tracking.
                    log.critical ("unable to get order details for pending order(%s)"%(order.id))
                    
    def update_market_states (self):
        '''
        Desc: 1. Update/refresh the various market states (rate, etc.)
              2. perform any pending trades (stop requests)
              3. Cancel/timeout any open orders if need be
        '''
        
        if sims.backtesting_on == True:
            if self.tradeConfig.get("stop_loss_smart_rate", False) == True:
                self.order_book.smart_stop_loss_update_positions(self.get_market_rate(), self.tradeConfig["stop_loss_rate"])            
            return        
        
        #1.take profit handling, this is aggressive take profit, not waiting for candle period
        if self.tradeConfig.get("take_profit_enabled", False):           
            self._handle_take_profit ()
                
        now = time.time()
        if now >= self.cur_candle_time + self.candle_interval:
            candle = OHLC(long(now), self.O, self.H, self.L, self.get_market_rate(), self.V)
            log.info ("New candle identified %s"%(candle))
            self.add_new_candle (candle)             
            
        #2.update market states
        if (self.order_book.book_valid == False):
            log.debug ("Re-Construct the Order Book")
            self.order_book.reset_book()     
        #3.pending trades
        self._handle_pending_trade_reqs ()

        
    def add_new_candle (self, candle):
        """
            Desc: Identify a new candle and add to the market data
                    This will result in calculating and indicators and
                    strategies and may result in generating trade signals
        """
        # Do not add new candles if backtesting is running
        if sims.backtesting_on == True:
            return
                    
        self.market_indicators_data.append({'ohlc': candle})
        self.market_strategies_data.append({})

#         self.cur_candle_time = candle.time
        self._calculate_all_indicators(self.num_candles)
        self._process_all_strategies(self.num_candles)
        self.num_candles += 1
        self.cur_candle_time = candle.time
        self.cur_candle_vol = candle.volume
        
        cur_rate = self.get_market_rate()
        # bit of conservative approach for smart-SL. update SL only on candle time
        if self.tradeConfig["stop_loss_smart_rate"] == True:
            self.order_book.smart_stop_loss_update_positions(cur_rate, self.tradeConfig["stop_loss_rate"])
                    
        self.O = self.H = self.L = self.C = cur_rate
        self.V = 0

        #save to db
        self.candlesDb.db_save_candle(candle)
        self.new_candle = True
        
                
    def generate_trade_signal (self, idx=-1):
        """ 
        Do all the magic to generate the trade signal
        params : exchange, product
        return : trade signal (-3..0..3)
                 -3 strong sell
                 +3 strong buy
        """
        signal = self.decision.generate_signal((idx if idx != -1 else (self.num_candles-1)))
        
        if signal != 0:
            log.info ("Generated Trade Signal(%d) for product(%s) idx(%d)"%(signal, self.product_id, idx))  
        else:
            log.debug ("Generated Trade Signal(%d) for product(%s) idx(%d)"%(signal, self.product_id, idx))            
                
        #processed the new candle
        self.new_candle = False
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
        trade_req_list = []        
#         exchange_name = self.exchange.name
#         ignore_file = "override/%s_%s.ignore"%(exchange_name, self.product_id)
#         #Override file name = override/TRADE_<exchange_name>.<product>
#         if (os.path.isfile(ignore_file)):
#             log.info("Ignore file present for product. Skip processing! "+ignore_file)
#             return


        #get manual trade reqs if any
        #trade_req_list = self._get_manual_trade_req ()
        
        # Now generate auto trade req list
        log.info ("Trade Signal strength:"+str(signal))
        trade_req_list += self._generate_trade_request(signal)
        #validate the trade Req
        if (len(trade_req_list)):
            self._execute_market_trade(trade_req_list)
    
    def close_all_positions(self):
        log.info ("finishing trading session; selling all acquired assets")
        # sell assets and come back to initial state
        trade_req_l = []
        while (True):
            position = self.order_book.get_closable_position()            
#                 asset_size = self.asset.get_asset_to_trade (1)
                
            if position:
#                 self.num_sell_req += 1                                     
                log.debug ("position: %s"%(str(position)))                    
                asset_size = position.buy.get_asset()
                if (asset_size <= 0):
                    log.critical ("Invalid open position for closing: position: %s"%str(position))
                    raise Exception("Invalid open position for closing??")
                log.debug ("Generating SELL trade_req with asset size: %s"%(str(asset_size)))       
                trade_req_l.append(TradeRequest(Product=self.product_id,
                                  Side="SELL",
                                   Size=round(Decimal(asset_size),8),
                                   Fund=round(Decimal(0), 8),                                   
                                   Type="market",
                                   Price=round(Decimal(0), 8),
                                   Stop=0, id=position.id))
            else:                              
                break
        self._execute_market_trade(trade_req_l)
############# Market Class Def - end ############# 

# Feed Q routines
feedQ = Queue.Queue()
def feed_enQ (market, msg):
    log.debug ("-------feed_enQ msg -------")    
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

def get_market_by_product (exchange_name, product_id):
    for market in OldMonk_market_list:
        if market.product_id == product_id and market.exchange_name == exchange_name:
            return market
        
def market_init (exchange_list, get_product_config_hook):
    '''
    Initialize per exchange, per product data.
    This is where we want to keep all the run stats
    '''
    global OldMonk_market_list
    
    for exchange in exchange_list:
        exchange.get_product_config = get_product_config_hook
        products = exchange.get_products()
        if products:
            for product in products:
                #init new Market for product
                try:
                    market = Market(product=product, exchange=exchange)
                except Exception:
                    log.critical ("Unable to get Market for exchange: %s product: %s"%(exchange.name, product['id']))
                else:
                    market = exchange.market_init (market)
                    if (market == None):
                        log.critical ("Market Init Failed for exchange: %s product: %s"%(exchange.name, product['id']))
                    else:
    #                     tradingConfig, decisionConfig = get_product_config_hook(exchange.name, product['id'])
    #                     if tradingConfig == None or decisionConfig == None:
    #                         log.critical ("Invalid product config")
    #                         raise Exception ("Invalid product config")
    #                     market.tradeConfig = tradingConfig
    #                     market.decisionConfig = decisionConfig
                        log.info ("market init success for exchange (%s) product: %s"%(exchange.name, product['id']))
                        OldMonk_market_list.append(market)
        else:
            log.error ("No products found in exchange:%s"%(exchange.name))
                 
def market_setup (restart=False):
    '''
    Setup market states.
    This is where we want to keep all the run stats
    '''
    global OldMonk_market_list
    
    if not len (OldMonk_market_list):
        log.critical("No Markets configured. Nothing to do!")
        exit (0)
    
    for market in OldMonk_market_list:
        status = market.market_setup (restart)
        if (status == False):
            log.critical ("Market Init Failed for market: %s"%(market.name))
            return False
        else:
            log.info ("Market setup completed for market: %s"%(market.name))
        
    if sims.import_only:
        log.info ("import_only! skip rest of setup")
        return
                
    log.info ("market setup complete for all markets, init decision engines now")
    for market in OldMonk_market_list:            
        status = market.decision_setup (OldMonk_market_list)
        if (status == False):
            log.critical ("decision_setup Failed for market: %s"%(market.name))
            return False
        else:
            log.info ("decision_setup completed for market: %s"%(market.name))
                        
def get_all_market_stats ():
    market_stats = {}
    for market in OldMonk_market_list:        
        market_stats[market.name] = json.loads(str(market))
    return market_stats

MARKET_STATS_FILE = "data/stats_market_%s_%s.json"
TRADE_STATS_FILE = "data/stats_traded_orders_%s.json"
POSITION_STATS_FILE = "data/stats_positions_%s_%s.json"        

def display_market_stats (fd = sys.stdout):
    global OldMonk_market_list
    if sys.stdout != fd:
        fd.write("\n\n*****Market statistics*****\n")
    for market in OldMonk_market_list:        
        fd.write(str("\n%s\n\n"%str(market)))
def flush_all_stats ():
    display_market_stats()
    
    for market in OldMonk_market_list:
        with open(MARKET_STATS_FILE%(market.exchange_name, market.product_id), "w") as fd:
            fd.write(str("\n%s\n\n"%str(market)))      
        with open(POSITION_STATS_FILE%(market.exchange_name, market.product_id), "w") as fd:
            market.order_book.dump_positions(fd)
            
#EOF