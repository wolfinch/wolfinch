#
#  Wolfinch Auto trading Bot
#  Desc:  exchange interactions Simulation
#
#  Copyright: (c) 2017-2019 Joshith Rayaroth Koderi
#  This file is part of Wolfinch.
# 
#  Wolfinch is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  Wolfinch is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with Wolfinch.  If not, see <https://www.gnu.org/licenses/>.

import sys
# import json
from bintrees import RBTree
# from decimal import Decimal
from sortedcontainers import sorteddict
from utils import getLogger
import stats
import db
import sims
from .order import Order

log = getLogger('ORDER-BOOK')
log.setLevel(log.CRITICAL)

class Position(object):
    def __init__(self, id=None, buy=None, sell=None, profit=0, stop_loss=0,
                  take_profit=0, open_time=None, closed_time=None, status=""):
        self.id     = id
        self.buy     = buy
        self.sell    = sell
        self.profit = profit
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.open_time = open_time
        self.closed_time = closed_time
        self.status = status  #'open'|closed|close_pending
        self._dirty = True
        
    def add_buy(self, order):
        if order == None:
            return
        self.buy = order
        self.update_state("open")
        self.open_time = order.create_time
    
    def add_sell(self, order):
        if order == None:
            return
        self.sell = order
        self.closed_time = order.create_time
    
    def update_state(self, status):
        if status == "open" or status == "close_pending" or status == "closed":
            self.status = status
            if status == "closed":
                self.profit = float((self.sell.get_price() - self.buy.get_price())*self.sell.get_asset())
        else:
            log.critical("Unknown position status(%s)"%(status))
            raise Exception("Unknown position status(%s)"%(status))
    def get_profit(self):
        return self.profit
    
    def set_stop_loss(self, stop_loss):
        self.stop_loss = stop_loss
        self._dirty = True
        log.debug("setting stop_loss(%f) for position."%(stop_loss))
                     
    def get_stop_loss(self):
        return self.stop_loss
    def set_take_profit(self, take_profit):
        self.take_profit = take_profit
        log.debug("setting take_profit(%f) for position."%(self.take_profit))
    def get_take_profit(self):
        return self.take_profit
    def __str__(self):
        buy_str = str(self.buy) if self.buy else "null"
        sell_str = str(self.sell) if self.sell else "null"
        return """{\n"id":"%s", "status":"%s", "open_time":"%s", "closed_time":"%s", "profit": %f, "stop_loss": %f, "take_profit":%f,
"buy":%s\n,"sell":%s\n}"""%(self.id, self.status, self.open_time, self.closed_time, round(self.profit,4), round(self.stop_loss,4),
                             round(self.take_profit,4),
                            buy_str, sell_str)
    def __repr__(self):
        return self.__str__()
        

class OrderBook():

    def __init__(self, market=None, bids=None, asks=None, log_to=None):
        self._asks = RBTree()
        self._bids = RBTree()
        self.book_valid = False
        self.new_book(bids, asks)
        self._sequence = -1
        self.market = market
        self._log_to = log_to
        if self._log_to:
            assert hasattr(self._log_to, 'write')
        # My order Details
        self.total_order_count = 0
        self.total_open_order_count = 0
        self.pending_buy_orders_db = {}
        self.pending_sell_orders_db = {}
        self.traded_buy_orders_db = {}
        self.traded_sell_orders_db = {}
        
        # positions
        self.all_positions =[]
        self.open_positions =[]
        self.close_pending_positions = {}
        self.closed_positions =[]
        
        self.orderDb    = db.OrderDb(Order, market.exchange_name, market.product_id)
        self.positionsDb = db.PositionDb(Position, market.exchange_name, market.product_id)
        #stop loss handling
        self.sl_dict = sorteddict.SortedDict()
        
        #take profit handling
        self.tp_dict = sorteddict.SortedDict()
        
        #trade Reqs
        self.pending_trade_req =[]  # TODO: FIXME: jork: this better be a nice AVL tree of sort
    def __str__(self):
        return """
{"position_all": %d, "open": %d, "close_pending": %d, "closed": %d}"""%(len(self.all_positions), len(self.open_positions),
                                len(self.close_pending_positions), len(self.closed_positions))
                    
    def add_pending_trade_req(self, trade_req):
        self.pending_trade_req.append(trade_req)
    def remove_pending_trade_req(self, trade_req):
        # primitive
        self.pending_trade_req.remove(trade_req)
        
    def open_position(self, buy_order):
        #open positions with buy orders only(we don't support 'short' now)
#         log.debug("open_position order: %s"%(buy_order))
        position = Position(id=buy_order.id)
        position.add_buy(buy_order)
        if self.market.tradeConfig["stop_loss_enabled"]:
            self.add_stop_loss_position(position, buy_order.get_price(), self.market.tradeConfig["stop_loss_rate"], buy_order.stop)
        if self.market.tradeConfig["take_profit_enabled"]:
            self.add_take_profit_position(position, buy_order.get_price(), self.market.tradeConfig["take_profit_rate"], buy_order.profit)
                
        self.all_positions.append(position)
        self.open_positions.append(position)
#         log.debug("\n\n\n***open_position: open(%d) closed(%d) close_pend(%d)"%(len(self.open_positions), len(self.closed_positions), len(self.close_pending_positions)))
        # save pos to db
        self.positionsDb.db_save_position(position)
          
    def get_closable_position(self):
        log.info("get_closable_position ")
            
        #get last open position for now
        # TODO: FIXME: This may not be the best way. might cause race with below api with multi thread/multi exch
        pos = None
        if len(self.open_positions):
            if self.market.tradeConfig["stop_loss_enabled"]:
                log.info("Finding closable position from _stop_loss_ pool.")
                pos = self.pop_stop_loss_position()
            if pos == None:
                try:
                    pos = self.open_positions.pop()
                except IndexError:
                    log.error("unable to find open position to close")
                    return None
                log.info("Found closable position from _regular_ pool. pos: %s"%(str(pos)))
            else:
                log.info("Found closable position from _stop_loss_ pool. pos: %s"%(str(pos)))
                self.open_positions.remove(pos)
            if(self.close_pending_positions.get(pos.id)):
                log.critical("""Position already close pending \npos:%s
                     close_pending_positions: %s
                     open_positions: %s"""%(str(pos), str(self.close_pending_positions), str(self.open_positions)))
                raise Exception("Duplicate close pending position")
            
            if self.market.tradeConfig["take_profit_enabled"]:
                self.pop_take_profit_position(pos)
                  
            self.close_pending_positions[pos.id] = pos
#         log.debug("\n\n\n***get_closable_position: open(%d) closed(%d) close_pend(%d) \n pos: %s"%(
#             len(self.open_positions), len(self.closed_positions), len(self.close_pending_positions), pos))
        return pos
        
    def close_position_pending(self, sell_order):
        # Intentionally _not_ updating the pos_db here. Yes, There is a case of wrong pos state if we go down come back during this state
        # TODO: FIXME: This may not be the best way. might cause race with below api with multi thread/multi exch
        log.info(" order:%s"%(sell_order.id))
#         log.debug("\n\n\n***: open(%d) closed(%d) close_pend(%d)\n"%(
#             len(self.open_positions), len(self.closed_positions), len(self.close_pending_positions)))
        pos = self.close_pending_positions.get(sell_order.id)
        if pos:
            log.info(": sell order(%s) already in pending_list. do nothing"%(sell_order.id))
            return pos
        #find a close_pending pos without sell attached.
        k = sell_order._pos_id
        if not k:
            log.critical("*****Invalid pos_id attached to order:%s**** \n may be an outside order"%(sell_order.id))
            raise Exception("Invalid pos_id attached to order")
        pos = self.close_pending_positions.get(k)
        if pos:
            #find the pos without sell attached. and reinsert after attach
#             log.debug("pos:\n%s"%(pos))
            if pos.sell == None:
                pos.add_sell(sell_order)
                pos.update_state("close_pending")
                del(self.close_pending_positions[k])
                self.close_pending_positions[sell_order.id] = pos

#                 log.debug("\n\n\n***: open(%d) closed(%d) close_pend(%d)"%(len(self.open_positions), len(self.closed_positions), len(self.close_pending_positions)))
                return pos
            else:
                log.critical("Wrong sell attached to pos:%s"%(pos))
                raise Exception("Wrong sell attached to pos")
        else:
            #something is very wrong
            log.critical("Unable to find pending position for close id: %s"%(sell_order.id))
            raise Exception("Unable to find pending position for close")
    def close_position_failed(self, pos_id):
        log.info("close_position_failed order: %s"%(pos_id))
#         log.debug("\n\n\n***close_position_failed: open(%d) closed(%d) close_pend(%d)"%(len(self.open_positions), len(self.closed_positions), len(self.close_pending_positions)))
           
#         id = sell_order.id
        position = self.close_pending_positions.get(pos_id)
        if position:
            position.sell = None
            self.close_pending_positions.pop(pos_id, None)
            self.open_positions.append(position)
            if self.market.tradeConfig["stop_loss_enabled"]:
                self.add_stop_loss_position(position, position.buy.get_price(),
                                             self.market.tradeConfig["stop_loss_rate"], position.get_stop_loss())
            if self.market.tradeConfig["take_profit_enabled"]:
                self.add_take_profit_position(position, position.buy.get_price(),
                                               self.market.tradeConfig["take_profit_rate"], position.get_take_profit())
        else:
            log.critical("Unable to get close_pending position. order_id: %s"%(pos_id))
    def close_position(self, sell_order):
        log.info("close_position order: %s"%(sell_order.id))
        id = sell_order.id
        position = self.close_pending_positions.pop(id, None)
        if position:
            position.add_sell(sell_order)
            position.update_state("closed")
            profit = position.get_profit()
            self.market.fund.current_realized_profit += profit
            if profit > 0 :
                self.market.num_success_trade += 1
            else:
                self.market.num_failed_trade += 1
            self.closed_positions.append(position)
                
                #update position
            self.positionsDb.db_save_position(position)
            log.info("position closed pos: %s"%(str(position)))
        else:
            log.critical("Unable to get close_pending position. order_id: %s"%(sell_order.id))
#         log.debug("\n\n\n***close_position: open(%d) closed(%d) close_pend(%d)\n pos:%s"%(
#             len(self.open_positions), len(self.closed_positions), len(self.close_pending_positions), position))
            
    def add_stop_loss_position(self, position, market_rate, sl_rate, stop_price=0):
        if stop_price == 0:
            stop_price = float(round(market_rate*(1 - sl_rate*float(.01)), 4))
        
        position.set_stop_loss(stop_price)
        
        pos_list = self.sl_dict.get(stop_price, None)
        if pos_list == None:
            pos_list =[]
            self.sl_dict[stop_price] = pos_list
        pos_list.append(position)
        
        
    def add_stop_loss_position_list(self, stop_price, position_l):
        [pos.set_stop_loss(stop_price) for pos in position_l]
        pos_list = self.sl_dict.get(stop_price, None)
        if pos_list == None:
            pos_list =[]
            self.sl_dict[stop_price] = pos_list
        pos_list+=position_l
    
    def remove_all_positions_at_stop(self, stop_price):
        return self.sl_dict.pop(stop_price, None)
           
    def smart_stop_loss_update_positions(self, market_rate, sl_rate):
        new_sl = float(round(market_rate*(1 - sl_rate*float(.01)), 4))
        
        key_list = list(self.sl_dict.irange(maximum=new_sl, inclusive=(False, False)))
        
        for key in key_list:
#             log.critical("new_sl: %d key: %d"%(new_sl, key))
            pos_list = self.sl_dict.pop(key)
            self.add_stop_loss_position_list(new_sl, pos_list)

    def db_commit_dirty_positions(self):
        dirty_pos_list =[]
        for pos in self.all_positions:
            if pos._dirty == True:
                pos._dirty = False
                dirty_pos_list.append(pos)
        
        if len(dirty_pos_list):
            log.debug("commit positions to db")
            # save pos to db
            self.positionsDb.db_save_positions(dirty_pos_list)
        
    def pop_stop_loss_position(self, pos=None):
        try:
            sl_price, pos_list = 0, None
            if pos :
                sl_price = pos.get_stop_loss()
                pos_list = self.sl_dict.get(sl_price)
            else:
                #get the lowest in the sorted SL list
                sl_price, pos_list = self.sl_dict.peekitem(index=0)
#             log.debug("pop position at sl_price:%d"%(sl_price))
            if pos_list and len(pos_list):
                if pos:
                    pos_list.remove(pos)
                else:
                    pos = pos_list.pop()
                if len(pos_list) == 0:
                    del(self.sl_dict[sl_price])
            return pos
        except (IndexError, ValueError):
            return None
    def get_stop_loss_positions(self, market_rate):
        sl_pos_list =[]
        
        key_list = list(self.sl_dict.irange(minimum=market_rate, inclusive=(True, True)))
#         log.critical("slPrice: %d"%market_rate)
#         log.critical("key_list :%s"%(key_list))
        
        for key in key_list:
            pos_list = self.sl_dict.pop(key)
            sl_pos_list += pos_list
            for pos in pos_list:
                self.open_positions.remove(pos)
                if(self.close_pending_positions.get(pos.id)):
                    log.critical("""Position already close pending \npos:%s
                     close_pending_positions: %s
                     open_positions: %s"""%(str(pos), str(self.close_pending_positions), str(self.open_positions)))
                    raise Exception("Duplicate close pending position")
                self.close_pending_positions[pos.id] = pos
                # remove pos from take profit points
                self.pop_take_profit_position(pos)
        self.market.num_stop_loss_hit += len(sl_pos_list)
        
#         if len(sl_pos_list):
#             log.critical("num_stop_loss_hit: %d slPrice: %d"%(len(sl_pos_list), market_rate))
        
        return sl_pos_list

    def get_take_profit_positions(self, market_rate):
        tp_pos_list =[]
        
        key_list = list(self.tp_dict.irange(maximum=market_rate, inclusive=(True, True)))
        
        for key in key_list:
            pos_list = self.tp_dict.pop(key)
            tp_pos_list += pos_list
            for pos in pos_list:
                self.open_positions.remove(pos)
                if(self.close_pending_positions.get(pos.id)):
                    log.critical("""Position already close pending \npos:%s
                     close_pending_positions: %s
                     open_positions: %s"""%(str(pos), str(self.close_pending_positions), str(self.open_positions)))
                    raise Exception("Duplicate close pending position")
                self.close_pending_positions[pos.id] = pos
                # remove pos from take profit points
                self.pop_stop_loss_position(pos)
                
        self.market.num_take_profit_hit += len(tp_pos_list)
        return tp_pos_list
            
            
    def add_take_profit_position(self, position, market_rate, tp_rate, tp_price=0):
        if tp_price == 0:
            new_tp = float(round(market_rate*(1 + tp_rate*float(.01)), 4))
        
        position.set_take_profit(new_tp)
        pos_list = self.tp_dict.get(new_tp, None)
        if pos_list == None:
            pos_list =[]
            self.tp_dict[new_tp] = pos_list
        pos_list.append(position)
        log.debug("add take profit(%d) market_rate:(%d)"%(new_tp, market_rate))
        
    def pop_take_profit_position(self, pos=None):
        try:
            tp_price, pos_list = 0, None
            if pos :
                tp_price = pos.get_take_profit()
                pos_list = self.tp_dict.get(tp_price)
            else:
                tp_price, pos_list = self.tp_dict.peekitem(0)
#             log.debug("pop position at sl_price:%d"%(sl_price))
            if pos_list and len(pos_list):
                if pos:
                    pos_list.remove(pos)
                else:
                    pos = pos_list.pop()
                if len(pos_list) == 0:
                    del(self.tp_dict[tp_price])
            return pos
        except (IndexError, ValueError):
            return None
                
    def get_all_pending_orders(self):
        pending_order_list =[]
        pending_order_list += list(self.pending_buy_orders_db.values())
        pending_order_list += list(self.pending_sell_orders_db.values())
        return pending_order_list
        
    def add_or_update_pending_buy_order(self, order):
        id = order.id
        cur_order = self.pending_buy_orders_db.get(id)
        if not cur_order:
            self.total_open_order_count += 1
            self.total_order_count += 1
        else:
            #copy required fields
            order.stop = cur_order.stop
            order.profit = cur_order.profit
        self.pending_buy_orders_db[id] = order
    def get_pending_buy_order(self, order_id):
        return self.pending_buy_orders_db.get(order_id)
    def add_traded_buy_order(self, order):
        cur_order = self.pending_buy_orders_db.get(order.id)
        if cur_order:
            #copy required fields            
            order.stop = cur_order.stop
            order.profit = cur_order.profit        
        self.total_open_order_count -= 1
        del(self.pending_buy_orders_db[order.id])
        self.traded_buy_orders_db[order.id] = order
        #if this is a successful order, we have a new position open
        if order.status == "filled":
            self.open_position(order)
            
    def get_traded_buy_order(self, order_id):
        return self.traded_buy_orders_db.get(order_id)
    def add_or_update_pending_sell_order(self, order):
        id = order.id
        if not self.pending_sell_orders_db.get(id):
            self.total_open_order_count += 1
            self.total_order_count += 1
        self.pending_sell_orders_db[id] = order
            
    def get_pending_sell_order(self, order_id):
        self.pending_sell_orders_db.get(order_id)
    def add_traded_sell_order(self, order):
        del(self.pending_sell_orders_db[order.id])
        self.total_open_order_count -= 1
        self.traded_sell_orders_db[order.id] = order
        #close/reopen position
        #TODO: TBD: more checks required??
        if order.status == "filled":
            log.debug("closed position order: %s"%(order.id))
            self.close_position(order)
        else:
            log.critical("closed position failed order: %s"%(order))
            self.close_position_failed(order.id)
    def get_traded_sell_order(self, order_id):
        return self.traded_sell_orders_db.get(order_id)
            
    def add_order_list(self, bids, asks):
        if(asks):
            self.add_asks(asks)
        if(bids):
            self.add_bids(bids)
            
    def clear_order_book(self):
        log.info("clearing older states")
        self.orderDb.clear_order_db()
        self.positionsDb.clear_position_db()
                
    def restore_order_book(self):
        # TODO: FIXME:  Not considering pending state orders
        
        if(sims.simulator_on):
            #don't do order db init for sim
            return None
        
        log.info("Restoring positions and orders")
        
        #1. Retrieve states back from Db
        order_list = self.orderDb.get_all_orders()
        
        if not order_list:
            log.info("no orders to restore")
        else:
            # restore orders
            log.info("Restoring %d orders"%(len(order_list)))
            for order in order_list:
    #             order_status = order.status_type
                order_side = order.side
                
                log.info("restoring order: %s side: %s"%(order.id, order_side))
                self.total_order_count += 1
                if order_side == 'buy':
                    self.traded_buy_orders_db[order.id] = order
                else:
                    self.traded_sell_orders_db[order.id] = order
                
        # restore positions
        pos_list = self.positionsDb.db_get_all_positions(self.orderDb)
#         log.critical("mapping: %s"%(str(self.positionsDb.mapping)))
        if not pos_list:
            log.info("no positions to restore")
            return
        
        log.info("Restoring %d positions"%(len(pos_list)))
        for pos in pos_list:
            log.debug("restoring position(%s)"%(pos.id))
            self.all_positions.append(pos)
            if pos.status == "open":
                self.open_positions.append(pos)
                if self.market.tradeConfig["stop_loss_enabled"]:
                    self.add_stop_loss_position(pos, pos.buy.get_price(),
                                                 self.market.tradeConfig["stop_loss_rate"], pos.get_stop_loss())
                if self.market.tradeConfig["take_profit_enabled"]:
                    self.add_take_profit_position(pos, pos.buy.get_price(),
                                                   self.market.tradeConfig["take_profit_rate"], pos.get_take_profit())
            else:
                self.closed_positions.append(pos)
        
        log.info("all positions and orders are restored")
#         sys.exit()
                
    def get_positions (self, from_time=0, to_time=0):
        log.info("get positions ", from_time, to_time)
        return self.all_positions[:]
        
    def dump_traded_orders(self, fd=sys.stdout):
        traded = str(list(self.traded_buy_orders_db.values()) + list(self.traded_sell_orders_db.values()))
        fd.write(traded)
    def dump_positions(self, fd=sys.stdout):
        fd.write(str(self.all_positions))
#
#     def on_sequence_gap(self, gap_start, gap_end):
#         self.reset_book()
#         print('Error: messages missing({} - {}). Re-initializing  book at sequence.'.format(
#             gap_start, gap_end, self._sequence))


####### Public API #######
    def add_or_update_my_order(self, order):
        # simplified order state machine :[open, filled, canceled]
        # this rework is assumed an abstraction and handles only simplified order status
        # if there are more order states, it should be handled/translated in the exch impl.
        # linked to market.order_status_update()
#         '''
#         Handle a new order update msg
#         return : order
#         '''
        if(not order):
            return None
        order_id = order.id
        order_status = order.status
        order_side = order.side
        if(not order_id):
            log.critical("Invalid order_id: status:%s side: %s" %(order_status, order_side))
            raise Exception("Invalid order_id: status:%s side: %s" %(order_status, order_side))
            
        if(order_side == 'buy'):
            # see if this is a late/mixed up state msg for an already done order. What we do here, may not be correct
            if self.get_traded_buy_order(order_id):
                log.critical("********(%s) order done already, but(%s) state msg recvd, ignore for now, FIXME: FIXME:"%(order_side, order_status))
                return None
            # insert/replace the order
            if(order_status == 'filled' or order_status == 'canceled'):
                # a previously placed order is completed, remove from open order, add to completed orderlist
                self.add_traded_buy_order(order)
                log.debug("Buy order Done: total_order_count: %d "
                       "total_open_order_count: %d "
                       "traded_buy_orders_count: %d" %(self.total_order_count,
                                                       self.total_open_order_count,
                                                       len(self.traded_buy_orders_db)))
            elif(order_status == 'open'):
                # Nothing much to do for us here
                log.info("Buy order_id(%s) Status: %s" %(str(order_id), order_status))
                self.add_or_update_pending_buy_order(order)
            else:
                log.critical("UNKNOWN buy order status: %s" %(order_status))
                raise Exception("UNKNOWN buy order status: %s" %(order_status))
        elif(order_side == 'sell'):
            # see if this is a late/mixed up state msg for an already done order. What we do here, may not be correct
            if self.get_traded_sell_order(order_id):
                log.critical("********(%s) order done already, but(%s) state msg recvd, ignore for now, FIXME: FIXME:"%(order_side, order_status))
                return None
            # insert/replace the order
            if(order_status == 'filled' or order_status == 'canceled'):
                # a previously placed order is completed, remove from open order, add to completed orderlist
                self.add_traded_sell_order(order)
                log.debug("Sell order Done: total_order_count: %d "
                       "total_open_order_count: %d "
                       "traded_sell_orders_count: %d" %(self.total_order_count,
                                                       self.total_open_order_count,
                                                       len(self.traded_sell_orders_db)))
            elif(order_status == 'open'):
                # Nothing much to do for us here
                log.info("Sell order_id(%s) Status: %s" %(str(order_id), order_status))
                self.add_or_update_pending_sell_order(order)
                self.close_position_pending(order)
            else:
                log.critical("UNKNOWN sell order status: %s" %(order_status))
                raise Exception("UNKNOWN buy order status: %s" %(order_status))
        else:
            log.critical("Invalid order :%s" %(order))
            raise Exception("Invalid order :%s" %(order))
#         log.debug("Order: %s\n"%(str(order)))
        
        #Add the successful order to the db
        self.orderDb.db_add_or_update_order(order)
        stats.stats_update_order(self.market, order)
        return order

    def new_book(self, bids, asks):
        log.info("Building new order book")
        if(bids and len(bids)) or(asks and len(asks)):
            self.add_order_list(bids, asks)
            self.book_valid = True
        else :
            self.book_valid = False

    def reset_book(self):
        self._asks = RBTree()
        self._bids = RBTree()
        res = self.market.exchange.get_product_order_book(self.market.product_id, level=3)
        # log.debug("%s"%(str(res)))
        if res == None:
            log.error("Unable to get orderbook for exchange(%s) product: %s"%(self.market.exchange.name, self.market.product_id))
            return
        for bid in res['bids']:
            new_size = float(bid[1])
            price = float(bid[0])
            new_size += float((self.get_bids(price) or 0))
            self.set_bids(price, new_size)
        for ask in res['asks']:
            new_size = float(ask[1])
            price = float(ask[0])
            new_size += float((self.get_asks(price) or 0))
            self.set_asks(price, new_size)
        self._sequence = float(res['sequence'])
        self.book_valid = True
#         print("asks: %s"%(str(self._asks)))
#         print("bids: %s"%(str(self._bids)))
                
    def add_asks(self, asks):
        '''
        asks =[[price, size]]
        '''
        for ask in asks:
            price = float(ask[0])
            size = float(ask[1])
            if size > 0:  # size > 0 add, size = 0 remove
                self.set_asks(price, size)
            else:
                if(self.get_asks(price)):
                    self.remove_asks(price)
            
    def get_ask(self):
        return self._asks.min_key()

    def get_asks(self, price):
        return self._asks.get(price)

    def remove_asks(self, price):
        self._asks.remove(price)

    def set_asks(self, price, asks):
        price = round(price, 8)
        asks = round(asks, 8)
        log.debug("set_asks: price: %g size: %g" %(price, asks))
        self._asks.insert(price, asks)

    def add_bids(self, bids):
        '''
        bids =[[price, size]]
        '''
        for bid in bids:
            price = float(bid[0])
            size = float(bid[1])
            if size > 0:  # size > 0 add, size = 0 remove
                self.set_bids(price, size)
            else:
                if(self.get_bids(price)):
                    self.remove_bids(price)
            
    def get_bid(self):
        return self._bids.max_key()

    def get_bids(self, price):
        return self._bids.get(price)

    def remove_bids(self, price):
        self._bids.remove(price)

    def set_bids(self, price, bids):
        price = round(price, 8)
        bids = round(bids, 8)
        log.debug("set_bid: price: %g size: %g" %(price, bids))
        self._bids.insert(price, bids)  # insert on RBtree is a replace for existing keys
                                                            
#EOF
