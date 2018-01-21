# '''
#  SkateBot Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''

from bintrees import RBTree
from decimal import Decimal

class OrderBook():
    def __init__(self, bids=None, asks=None, log_to=None):
        self._asks = RBTree()
        self._bids = RBTree()
        self.add_order_list (bids, asks)
        self._sequence = -1
        self._log_to = log_to
        if self._log_to:
            assert hasattr(self._log_to, 'write')
        
#                 
#     def reset_book(self):
#         self._asks = RBTree()
#         self._bids = RBTree()
#         res = self._client.get_product_order_book(product_id=self.product_id, level=2)        
#         for bid in res['bids']:
#             self.add({
#                 'id': bid[2],
#                 'side': 'buy',
#                 'price': Decimal(bid[0]),
#                 'size': Decimal(bid[1])
#             })
#         for ask in res['asks']:
#             self.add({
#                 'id': ask[2],
#                 'side': 'sell',
#                 'price': Decimal(ask[0]),
#                 'size': Decimal(ask[1])
#             })
#         self._sequence = res['sequence']
#         
#         
#     def on_sequence_gap(self, gap_start, gap_end):
#         self.reset_book()
#         print('Error: messages missing ({} - {}). Re-initializing  book at sequence.'.format(
#             gap_start, gap_end, self._sequence))

                    
    def add_order_list (self, bids, asks):
        if (asks):
            self.add_asks (asks)
        if (bids):            
            self.add_bids (bids)
                    
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
        self._bids.insert(price, bids) # insert on RBtree is a replace for existing keys
        
        
                                                            