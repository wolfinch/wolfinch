
'''
 SkateBot Auto trading Bot
 Desc: Order Class and TradeRequest class - implementation
 (c) Joshith Rayaroth Koderi
'''
from decimal import Decimal

#simple class to have the trade request (FIXME: add proper shape)
class TradeRequest:
#    ''' 
#        Desc: Common exchange neutral Trade Request
#            class {
#            product: <name>
#            side: <BUY|SELL>
#            type: <limit|market>
#            size: <SIZE crypto>
#            price: <limit/market-price>
#            }
#    '''   
    def __init__(self, Product, Side, Size, Type, Price, Stop):
        self.product = Product
        self.side = Side
        self.size = Size
        self.type = Type
        self.price = Price
        self.stop = Decimal(Stop or 0)
    def __str__(self):
        return "{'product':%s, 'side':%s, 'size':%g 'type':%s, 'price':%g, 'stop':%g}"%(
            self.product, self.side, self.size, self.type, self.price, self.stop)

class Order:
    '''
    Desc: Common/exchange neutral OrderStatus strucutre
    {
    id         : <order_id>
    product_id : <product-id>
    order_type : <limit|market>
    status_type: <pending|open|done|match|received|change|>
    status_reason: <filled|cancelled|rejected..>
    side         : <buy|sell>
    size         : <asset size>
    price        : <price>
    funds        : <total funds>
    time         : <order status time>
    }
    '''
    def __init__(self, order_id, product_id, status_type, order_type=None, status_reason=None,
                 side=None, request_size=0, filled_size=0, remaining_size=0, price=0, funds=0,
                 fees=0, create_time=None, update_time=None
                 ):
        self.id = order_id
        self.product_id = product_id
        self.order_type = order_type
        self.status_type =  status_type
        self.status_reason  = status_reason
        self.side = side
        self.request_size = Decimal (request_size)
        self.filled_size = Decimal(filled_size)
        self.remaining_size = Decimal(remaining_size)
        self.price = Decimal(price)
        self.funds = Decimal(funds)
        self.fees  = Decimal(fees)
        self.create_time  = create_time
        self.update_time = update_time
        
    def __str__ (self):
        return ("{'id':%s, 'product_id':%s, 'side':%s, 'order_type':%s, "
            "'status_type':%s, 'status_reason':%s, 'request_size':%s, "
            "'filled_size':%s, 'remaining_size':%s, 'price':%s, 'funds':%s, "
            "'fees':%s, 'create_time':%s, 'update_time':%s}")%(
            self.id, self.product_id, self.side, self.order_type, self.status_type,
             self.status_reason, self.request_size, self.filled_size, self.remaining_size,
             self.price, self.funds, self.fees, self.create_time, self.update_time)
    
#EOF
        