# '''
#  OldMonk Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''
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

import uuid
from bintrees import RBTree
from decimal import Decimal

from utils import getLogger

log = getLogger('ORDER-BOOK')
log.setLevel(log.CRITICAL)


class OrderBook():

    def __init__(self, market=None, bids=None, asks=None, log_to=None):
        self._asks = RBTree()
        self._bids = RBTree()
        self.book_valid = False
        self.new_book (bids, asks)
        self._sequence = -1
        self.market = market        
        self._log_to = log_to
        if self._log_to:
            assert hasattr(self._log_to, 'write')
        # My order Details    
        self.total_order_count = 0
        self.total_open_order_count = 0        
        self.open_buy_orders_db = {}
        self.open_sell_orders_db = {}
        self.traded_buy_orders_db = []
        self.traded_sell_orders_db = []
        self.pending_trade_req = []  # TODO: FIXME: jork: this better be a nice AVL tree or sort
                    
    def add_pending_trade_req(self, trade_req):
        self.pending_trade_req.append(trade_req)
        
    def remove_pending_trade_req(self, trade_req):
        # primitive 
        self.pending_trade_req.remove(trade_req)

    def add_order_list (self, bids, asks):
        if (asks):
            self.add_asks (asks)
        if (bids):            
            self.add_bids (bids)
                    
#         
#     def on_sequence_gap(self, gap_start, gap_end):
#         self.reset_book()
#         print('Error: messages missing ({} - {}). Re-initializing  book at sequence.'.format(
#             gap_start, gap_end, self._sequence))

####### Public API #######
        
    def add_or_update_my_order (self, order):
        '''
        Handle a new order update msg
        return : order
        '''
        if (not order):
            return None
        order_id = uuid.UUID(order.id)
        order_status = order.status_type
        order_side = order.side
        if (not order_id):
            log.critical ("Invalid order_id: status:%s side: %s" % (order_status, order_side))
            return None
        current_order = None
        if (order_side == 'buy'):
            current_order = self.open_buy_orders_db.get (order_id)
        else:
            current_order = self.open_sell_orders_db.get (order_id)
            
        if current_order != None:
            # Copy whatever available, new gets precedence
            # money, asset
            order.request_size = order.request_size or current_order.request_size
            order.price = order.price or current_order.price
            order.funds = order.funds or current_order.funds
            order.fees = order.fees or current_order.fees
            if order_status != 'done':
                order.remaining_size = order.remaining_size or current_order.remaining_size
            # other data
            order.create_time = order.create_time or current_order.create_time
            order.update_time = order.update_time or current_order.update_time
            order.order_type = order.order_type or current_order.order_type
            order.product_id = order.product_id or current_order.product_id
        else:
            # this is a new order for us (not necessary placed by us, hence need this logic here)
            log.debug ("New Order Entry To be Inserted: total_order_count: %d "
                       "total_open_order_count: %d " % (self.total_order_count, self.total_open_order_count))
            
        if (order_side == 'buy'):
            # insert/replace the order
            self.open_buy_orders_db[order_id] = order
            self.total_open_order_count += 1
            self.total_order_count += 1            
            if (order_status == 'done'):
                # a previously placed order is completed, remove from open order, add to completed orderlist
                del (self.open_buy_orders_db[order_id])
                self.total_open_order_count -= 1
                self.traded_buy_orders_db.append(order)
                log.debug ("Buy order Done: total_order_count: %d "
                       "total_open_order_count: %d "
                       "traded_buy_orders_count: %d" % (self.total_order_count,
                                                       self.total_open_order_count,
                                                       len(self.traded_buy_orders_db)))
            elif (order_status in ['pending', 'open', 'received', 'match']):
                # Nothing much to do for us here
                log.info ("Buy order_id(%s) Status: %s" % (str(order_id), order_status))                
            else:
                log.critical("UNKNOWN buy order status: %s" % (order_status))
                raise Exception("UNKNOWN buy order status: %s" % (order_status))
                return None
        elif (order_side == 'sell'):
            # insert/replace the order
            self.open_sell_orders_db[order_id] = order
            self.total_open_order_count += 1
            self.total_order_count += 1            
            if (order_status == 'done'):
                # a previously placed order is completed, remove from open order, add to completed orderlist      
                del (self.open_sell_orders_db[order_id])
                self.total_open_order_count -= 1
                self.traded_sell_orders_db.append(order)
                log.debug ("Sell order Done: total_order_count: %d "
                       "total_open_order_count: %d "
                       "traded_sell_orders_count: %d" % (self.total_order_count,
                                                       self.total_open_order_count,
                                                       len(self.traded_sell_orders_db)))    
            elif (order_status in ['pending', 'open', 'received', 'match']):
                # Nothing much to do for us here
                log.info ("Sell order_id(%s) Status: %s" % (str(order_id), order_status))
            else:
                log.critical("UNKNOWN sell order status: %s" % (order_status))
                raise Exception("UNKNOWN buy order status: %s" % (order_status))                
                return None
        else:
            log.critical("Invalid order :%s" % (order))
            raise Exception("Invalid order :%s" % (order))            
            return None
#         log.debug ("Order: %s\n"%(str(order)))
        return order
    
    ######### L2 Order book for Exchange, product ########
    def new_book (self, bids, asks):
        log.info ("Building new order book")
        if (bids and len(bids)) or (asks and len(asks)):
            self.add_order_list(bids, asks)            
            self.book_valid = True
        else :
            self.book_valid = False 

    def reset_book(self):
        self._asks = RBTree()
        self._bids = RBTree()
        res = self.market.exchange.get_product_order_book(self.market.product_id, level=3)
        # log.debug ("%s"%(str(res)))     
        if res == None:
            log.error ("Unable to get orderbook for exchange(%s) product: %s"%(self.market.exchange.name, self.market.product_id))
            return
        for bid in res['bids']:
            new_size = Decimal(bid[1]) 
            price = Decimal(bid[0])
            new_size += Decimal((self.get_bids(price) or 0))
            self.set_bids(price, new_size)
        for ask in res['asks']:
            new_size = Decimal(ask[1]) 
            price = Decimal(ask[0])
            new_size += Decimal((self.get_asks(price) or 0))
            self.set_asks(price, new_size)
        self._sequence = Decimal(res['sequence'])
        self.book_valid = True
#         print ("asks: %s"%(str(self._asks)))
#         print ("bids: %s"%(str(self._bids)))
                
    def add_asks (self, asks):
        ''' 
        asks = [ [price, size]]
        '''
        for ask in asks:
            price = Decimal(ask[0])
            size = Decimal(ask[1])
            if size > 0:  # size > 0 add, size = 0 remove
                self.set_asks(price, size)
            else:
                if (self.get_asks(price)):
                    self.remove_asks(price)                      
            
    def get_ask(self):
        return self._asks.min_key()

    def get_asks(self, price):
        return self._asks.get(price)

    def remove_asks(self, price):
        self._asks.remove(price)

    def set_asks(self, price, asks):
        price = round(price, 8)
        asks = round (asks, 8)
        log.debug ("set_asks: price: %g size: %g" % (price, asks))        
        self._asks.insert(price, asks)

    def add_bids (self, bids):
        ''' 
        bids = [ [price, size]]
        '''
        for bid in bids:
            price = Decimal(bid[0])
            size = Decimal(bid[1])
            if size > 0:  # size > 0 add, size = 0 remove
                self.set_bids(price, size)
            else:
                if (self.get_bids(price)):
                    self.remove_bids(price)      
            
    def get_bid(self):
        return self._bids.max_key()

    def get_bids(self, price):
        return self._bids.get(price)

    def remove_bids(self, price):
        self._bids.remove(price)

    def set_bids(self, price, bids):
        price = round(price, 8)
        bids = round (bids, 8)
        log.debug ("set_bid: price: %g size: %g" % (price, bids))
        self._bids.insert(price, bids)  # insert on RBtree is a replace for existing keys
                                                            
#EOF