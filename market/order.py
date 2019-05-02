
'''
 OldMonk Auto trading Bot
 Desc: Order Class and TradeRequest class - implementation
 (c) Joshith Rayaroth Koderi
'''
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from utils import getLogger
from decimal import Decimal
import db

Db = None #db.init_db()
log = getLogger ('ORDER')

Base = declarative_base()

# simple class to have the trade request (FIXME: add proper shape)
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
    def __init__(self, Product, Side, Size, Type, Price, Stop):
        self.product = Product
        self.side = Side
        self.size = Size
        self.type = Type
        self.price = Price
        self.stop = Decimal(Stop or 0)

    def __str__(self):
        return "{'product':%s, 'side':%s, 'size':%g 'type':%s, 'price':%g, 'stop':%g}" % (
            self.product, self.side, self.size, self.type, self.price, self.stop)


class Order (Base):
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
    __tablename__ = 'order_table' #TODO: FIXME: extend with market_product_id

#     prim_id = Column(Integer, primary_key=True)
    id = Column(String(64), index=True, nullable=False, primary_key=True)
    product_id = Column(String(64), index=True, nullable=False)
    order_type = Column(String(64), index=True, nullable=False)
    status_type = Column(String(64), index=True, nullable=False)
    status_reason = Column(String(64), index=True, nullable=True)
    side = Column(String(64), index=True, nullable=False)
    request_size = Column(Numeric, default=0)
    filled_size = Column(Numeric, default=0)
    remaining_size = Column(Numeric, default=0)
    price = Column(Numeric, default=0)
    funds = Column(Numeric, default=0)
    fees = Column(Numeric, default=0)
    create_time = Column(String(64))
    update_time = Column(String(64))    
        
    def __init__(self, order_id, product_id, status_type, order_type=None, status_reason=None,
                 side=None, request_size=0, filled_size=0, remaining_size=0, price=0, funds=0,
                 fees=0, create_time=None, update_time=None
                 ):
        self.id = order_id
        self.product_id = product_id
        self.order_type = order_type
        self.status_type = status_type
        self.status_reason = status_reason
        self.side = side
        self.request_size = Decimal (request_size)
        self.filled_size = Decimal(filled_size)
        self.remaining_size = Decimal(remaining_size)
        self.price = Decimal(price)
        self.funds = Decimal(funds)
        self.fees = Decimal(fees)
        self.create_time = create_time
        self.update_time = update_time
        
    def __str__ (self):
        return ("{'id':%s, 'product_id':%s, 'side':%s, 'order_type':%s, "
            "'status_type':%s, 'status_reason':%s, 'request_size':%s, "
            "'filled_size':%s, 'remaining_size':%s, 'price':%s, 'funds':%s, "
            "'fees':%s, 'create_time':%s, 'update_time':%s}") % (
            self.id, self.product_id, self.side, self.order_type, self.status_type,
             self.status_reason, self.request_size, self.filled_size, self.remaining_size,
             self.price, self.funds, self.fees, self.create_time, self.update_time)
            
    def DbSave (self):
        global Db
        if not Db:
            Db = db.init_db()
        log.info ("save order to db")
        Db.session.merge(self)
        Db.session.commit()
        
    def DbDelete (self):
        global Db
        if not Db:
            Db = db.init_db()
        log.info ("save order to db")
        Db.session.delete(self)
        Db.session.commit()        
        
    @classmethod        
    def DbGet (cls, order_id):
        global Db
        if not Db:
            Db = db.init_db()
        try:
            result = Db.session.query(cls).filter_by(id=order_id)
            if result:
                log.info ("get order from db")                
                return result.first()
        except Exception, e:
            print(e.message)
        return None 
    
    @classmethod
    def DbCreateTable (cls):
        global Db
        if not Db:
            Db = db.init_db()        
        try:
            if not Db.engine.dialect.has_table(Db.engine, cls.__tablename__):  # If table don't exist, Create.
                log.info ("table: %s does not exist, creating: %s"%(cls.__tablename__, cls.__table__ ))                
                Base.metadata.create_all(Db.engine, checkfirst=True)
            else:
                log.info ("table: %s exists, reflecting table: %s"%(cls.__tablename__, cls.__table__ ))                                
                Base.metadata.tables[cls.__tablename__]
        except Exception, e:
            print(e.message)
        return None
    
    @classmethod
    def DbDropTable(cls):
        global Db
        if not Db:
            Db = db.init_db()        
        try:
            log.info ("Dropping table %s"%cls.__tablename__)
            cls.__table__.drop(Db.engine)
        except Exception, e:
            print(e.message)
        return None                    
# EOF