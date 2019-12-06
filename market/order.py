
'''
 Wolfinch Auto trading Bot
 Desc: Order Class and TradeRequest and order class - implementation
(c) Wolfinch Bot
'''
from sqlalchemy.ext.declarative import declarative_base
from utils import getLogger
# from decimal import float

Db = None #db.init_db()
log = getLogger('ORDER')
log.setLevel(log.CRITICAL)

# Base = declarative_base()

# simple class to have the trade request(FIXME: add proper shape)
class TradeRequest:

#    '''
#        Desc: Common exchange neutral Trade Request
#            class {
#            product: <name>
#            side: <BUY|SELL>
#            type: <limit|market>
#            size: <SIZE Asset>
#            price: <limit/market-price>
#            }
#    '''
    def __init__(self, Product, Side, Size, Fund, Type, Price, Stop, id=None):
        self.id = id
        self.product = Product
        self.side = Side
        self.size = Size
        self.fund = Fund
        self.type = Type
        self.price = Price
        self.stop = float(Stop or 0)

    def __str__(self):
        return "{'product':%s, 'side':%s, 'size':%f, 'fund':%f, 'type':%s, 'price':%f, 'stop':%f}" %(
            self.product, self.side, self.size, self.fund, self.type, self.price, self.stop)


class Order(object):
    '''
    Desc: Common/exchange neutral OrderStatus structure
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
#     __tablename__ = 'order_table' #TODO: FIXME: extend with market_product_id
#
# #     prim_id = Column(Integer, primary_key=True)
#     id = Column(String(64), index=True, nullable=False, primary_key=True)
#     product_id = Column(String(64), index=True, nullable=False)
#     order_type = Column(String(64), index=True, nullable=False)
#     status_type = Column(String(64), index=True, nullable=False)
#     status_reason = Column(String(64), index=True, nullable=True)
#     side = Column(String(64), index=True, nullable=False)
#     request_size = Column(Numeric, default=0)
#     filled_size = Column(Numeric, default=0)
#     remaining_size = Column(Numeric, default=0)
#     price = Column(Numeric, default=0)
#     funds = Column(Numeric, default=0)
#     fees = Column(Numeric, default=0)
#     create_time = Column(String(64))
#     update_time = Column(String(64))
        
    def __init__(self, order_id, product_id, status, order_type=None,
                 side=None, request_size=0, filled_size=0, remaining_size=0, price=0, funds=0,
                 fees=0, create_time=None, update_time=None
                 ):
        self.id = order_id
        self.product_id = product_id
        self.order_type = order_type
        self.status = status
#         self.status_reason = status_reason
        self.side = side
        self.request_size = float(request_size)
        self.filled_size = float(filled_size)
        self.remaining_size = float(remaining_size)
        self.price = float(price)
        self.funds = float(funds)
        self.fees = float(fees)
        self.create_time = create_time
        self.update_time = update_time
        self._pos_id = 0
        
    def __str__(self):
        return("""{"id":"%s", "product_id":"%s", "side":"%s", "order_type":"%s",
"status":"%s", "request_size":%f,
"filled_size":%f, "remaining_size":%f, "price":%f, "funds":%f,
"fees":%f, "create_time":"%s", "update_time":"%s"}""") %(
            self.id, self.product_id, self.side, self.order_type, self.status,
            self.request_size, self.filled_size, self.remaining_size,
             self.price, self.funds, self.fees, self.create_time, self.update_time)
    def __repr__(self):
        return self.__str__()
            
    def get_price(self):
        return self.price
    def get_funds(self):
        return self.funds
    def get_asset(self):
        return self.filled_size
    def get_side(self):
        return self.side
        
#     def DbSave(self):
#         global Db
#         if not Db:
#             Db = db.init_db()
#         log.info("save order to db order:%s"%(str(self)))
#         Db.session.merge(self)
#         log.critical("mapping: %s"%(str(Db.session.mapping)))
#         Db.session.commit()
#
#     def DbDelete(self):
#         global Db
#         if not Db:
#             Db = db.init_db()
#         log.info("save order to db")
#         Db.session.delete(self)
#         Db.session.commit()
#
#     @classmethod
#     def DbGet(cls, order_id):
#         global Db
#         if not Db:
#             Db = db.init_db()
#         try:
#             result = Db.session.query(cls).filter_by(id=order_id)
#             if result:
#                 log.info("get order from db")
#                 return result.first()
#         except Exception, e:
#             print(e.message)
#         return None
#
#     @classmethod
#     def DbCreateTable(cls):
#         global Db
#         if not Db:
#             Db = db.init_db()
#         try:
#             if not Db.engine.dialect.has_table(Db.engine, cls.__tablename__):  # If table don't exist, Create.
#                 log.info("table: %s does not exist, creating: %s"%(cls.__tablename__, cls.__table__ ))
#                 Base.metadata.create_all(Db.engine, checkfirst=True)
#             else:
#                 log.info("table: %s exists, reflecting table: %s"%(cls.__tablename__, cls.__table__ ))
#                 Base.metadata.tables[cls.__tablename__]
#         except Exception, e:
#             print(e.message)
#         return None
#
#     @classmethod
#     def DbDropTable(cls):
#         global Db
#         if not Db:
#             Db = db.init_db()
#         try:
#             log.info("Dropping table %s"%cls.__tablename__)
#             cls.__table__.drop(Db.engine)
#         except Exception, e:
#             print(e.message)
#         return None
# EOF
