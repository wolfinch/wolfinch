# '''
#  SkateBot Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''

import uuid
from bintrees import RBTree
from decimal import Decimal

from utils import *

log = getLogger('OrderBook')
log.setLevel(log.INFO)

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
        self.pending_trade_req = []           #TODO: FIXME: jork: this better be a nice AVL tree or sort
                    
    def add_pending_trade_req(self, trade_req):
        self.pending_trade_req.append(trade_req)
        
    def remove_pending_trade_req(self, trade_req):
        #primitive 
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
        Handle a new order updae msg
        '''
        if (not order):
            return False
        order_id = uuid.UUID(order.get('id') or order.get('order_id'))
        order_status = order.get('status') or order.get('type')
        order_side   = order['side'] 
        if (order_side == 'buy'):
            if (order_status == 'done'):
                #a previously placed order is completed, remove from open order, add to completed orderlist
                log.info ("Buy order Done: id(%s)"%(str(order_id)))                
                if (self.open_buy_orders_db.get(order_id)):
                    del (self.open_buy_orders_db[order_id])
                    self.total_open_order_count -=1
                self.traded_buy_orders_db.append(order)
            elif (order_status ==  'pending') or (order_status ==  'open'): ####### TODO: FIXME: Add more conditions
                pass
            elif (order_status == 'match'):
                log.info ("Buy order match: id(%s)"%(str(order_id)))
            elif (order_status == 'received'):
                # this is a new order
                log.info ("Buy order received: id(%s)"%(str(order_id)))                
                self.open_buy_orders_db[order_id] = order
                self.total_open_order_count +=1
                self.total_order_count +=1
            else:
                log.critical("UNKNOWN buy order status: %s"%(order_status ))
                return False
        elif (order_side == 'sell'):
            if (order_status == 'done'):
                #a previously placed order is completed, remove from open order, add to completed orderlist
                log.info ("Sell order Done: id(%s)"%(str(order_id)))                
                if (self.open_sell_orders_db.get(order_id)):
                    del (self.open_sell_orders_db[order_id])
                    self.total_open_order_count -=1                    
                self.traded_sell_orders_db.append(order)
            elif (order_status ==  'pending') or (order_status ==  'open'): ####### TODO: FIXME: Add more conditions
                pass
            elif (order_status == 'match'):
                log.info ("Sell order match: id(%s)"%(str(order_id)))                
            elif (order_status == 'received'): 
                # this is a new order
                log.info ("Sell order received: id(%s)"%(str(order_id)))                                
                self.open_sell_orders_db[order_id] = order
                self.total_open_order_count +=1
                self.total_order_count +=1
            else:
                log.critical("UNKNOWN sell order status: %s"%(order_status ))
                return False
        else:
            log.error("Invalid order :%s"%(order))
            return False
        return True
    
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
        #log.debug ("%s"%(str(res)))     
        for bid in res['bids']:
            new_size = Decimal(bid[1]) 
            price = Decimal(bid[0])
            new_size +=  (self.get_bids(price) or 0)
            self.set_bids(price, new_size)
        for ask in res['asks']:
            new_size = Decimal(ask[1]) 
            price = Decimal(ask[0])
            new_size +=  (self.get_asks(price) or 0)
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
        log.debug ("set_asks: price: %g size: %g"%(price, asks))        
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
        log.debug ("set_bid: price: %g size: %g"%(price, bids))
        self._bids.insert(price, bids) # insert on RBtree is a replace for existing keys
        
        
                                                            