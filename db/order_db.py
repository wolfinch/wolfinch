#
# wolfinch Auto trading Bot
# Desc: order_db impl
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


from utils import getLogger
from .db import init_db, is_db_enabled
from sqlalchemy import *
from sqlalchemy.orm import mapper 
# import sys
# import sqlalchemy

log = getLogger ('ORDER-DB')
log.setLevel (log.ERROR)

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
# logging.getLogger('sqlalchemy.orm').setLevel(logging.DEBUG)
# logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)

# Order db is currently a dictionary, keyed with order.id (UUID)

class OrderDb(object):
    def __init__ (self, orderCls, exchange_name, product_id, read_only=False):
        self.OrderCls = orderCls
        self.db_enable = False
        self.ORDER_DB = {}
        
        if not is_db_enabled():
            # skip db init
            log.info ("sim on, skip db init")
#             self.db_enable = True
            return
        else:
            self.db_enable = True
        
        self.db = init_db(read_only)
#         self.market = market
        self.exchange_name = exchange_name
        self.product_id = product_id
        
        log.info ("init ordersdb")
        self.table_name = "order_%s_%s"%(self.exchange_name, self.product_id)
        if not self.db.engine.dialect.has_table(self.db.engine, self.table_name):  # If table don't exist, Create.
            # Create a table with the appropriate Columns
            log.info ("creating table: %s"%(self.table_name))
            self.table = Table(self.table_name, self.db.metadata,  
#                 Column('id', Integer, primary_key=True),
                Column('id', String(128), index=True, nullable=False, primary_key=True),
                Column('product_id', String(128)),
                Column('order_type', String(128)),
                Column('status', String(128)),
#                 Column('status_reason', String(128)),   
                Column('side', String(128)),
                Column('request_size', Numeric, default=0),
                Column('filled_size', Numeric, default=0),
                Column('remaining_size', Numeric, default=0),    
                Column('price', Numeric, default=0),
                Column('funds', Numeric, default=0),
                Column('fees', Numeric, default=0),                   
                Column('create_time', String(128)),
                Column('update_time', String(128)))
            # Implement the creation
            self.db.metadata.create_all(self.db.engine, checkfirst=True)   
        else:
            log.info ("table %s exists already"%self.table_name)            
            self.table = self.db.metadata.tables[self.table_name]
        try:
            # HACK ALERT: to support multi-table with same class on sqlalchemy mapping
            class OT (orderCls):
                def __init__ (self, c):
                    self.id = c.id
                    self.product_id = c.product_id if c.product_id else "null"
                    self.order_type = c.order_type if c.order_type else "null"
                    self.status = c.status if c.status else "null"
#                     self.status_reason = c.status_reason if c.status_reason else "null"
                    self.side = c.side if c.side else "null"
                    self.request_size = c.request_size                    
                    self.filled_size = c.filled_size
                    self.remaining_size = c.remaining_size
                    self.price = c.price
                    self.funds = c.funds
                    self.fees = c.fees                    
                    self.create_time = c.create_time
                    self.update_time = c.update_time
            self.orderCls = OT
            self.mapping = mapper(self.orderCls, self.table)
        except Exception as e:
            log.debug ("mapping failed with except: %s \n trying once again with non_primary mapping"%(e.message))
            raise e
    
    def _db_save_order (self, order):     
        
        c = self.orderCls(order)

#         log.debug ("Adding order to db t:%s \n\n o:%s \n\n m:%s \n\n c: %s"%(type(order), order, str(self.mapping), str(c)))
        self.db.session.merge (c)
        self.db.session.commit()
        
    def _db_save_orders (self, orders):
        log.debug ("Adding order list to db")

        for odr in orders:
            c = self.orderCls(odr)
            self.db.session.merge (c)
        self.db.session.commit()
        
    def _db_delete_order(self, order):
        c = self.orderCls(order)
        self.db.session.delete (c)
        self.db.session.commit()
        
    def _db_get_all_orders (self):        
        log.debug ("retrieving orders from db")
        res_list = []
        try:
            ResultSet = self.db.session.query(self.mapping).all()
            log.info ("Retrieved %d orders for table: %s"%(len(ResultSet), self.table_name))

            if ResultSet:
                log.info ("#%d order entries"%(len(ResultSet)))
                for order in ResultSet:
                    log.info ("inserting order: %s in cache"%(str(order.id)))
                    o = self.OrderCls(order.id, order.product_id, order.status, order_type=order.order_type,
                                      side=order.side,
                  request_size=order.request_size, filled_size=order.filled_size,
                  remaining_size=order.remaining_size, price=order.price, funds=order.funds,
                 fees=order.fees, create_time=order.create_time, update_time=order.update_time)
                    res_list.append(o)
            #clear cache now
            self.db.session.expire_all()                           
            return res_list
        except Exception as e:
            log.critical(e.message)

    def _db_get_order(self, order_id):
        order = None
        try:
            result = self.db.session.query(self.mapping).filter_by(id=order_id)
            if result:
                db_order = result.first()
            if db_order != None:
                log.info ("got order from db ")     
                order = self.OrderCls(db_order.id, db_order.product_id, db_order.status, order_type=db_order.order_type,
                                       side=db_order.side,
                  request_size=db_order.request_size, filled_size=db_order.filled_size,
                  remaining_size=db_order.remaining_size, price=db_order.price, funds=db_order.funds,
                 fees=db_order.fees, create_time=db_order.create_time, update_time=db_order.update_time)
            else:
                log.error ("order_id:%s not in Db"%(order_id))
            #clear cache now
            self.db.session.expire_all()                             
        except Exception as e:
            print(e.message)
        return order
                        
    def db_add_or_update_order (self, order):     
        log.debug ("Adding order to db")
        self.ORDER_DB [order.id] = order
        
        if (not self.db_enable):
            return
        self._db_save_order(order)
        
        
    def db_del_order (self, order):       
        log.debug ("Del order from db")    
        del(self.ORDER_DB[order.id])
        #TODO: FIXME: Handle Db here ??
         
        if (not self.db_enable):
            return
        self._db_delete_order(order)
        
    def db_get_order (self, order_id):
        log.debug ("Get order from db")
        order = self.ORDER_DB.get(order_id)  
        
        if (not self.db_enable):
            #skip Db
            return order
        
        if order == None:
            log.info ("order_id:%s not in cache, trying to get from db"%(order_id))
            order = self._db_get_order(order_id)
            if order:
                self.ORDER_DB [order.id] = order
        return order
        
    def get_all_orders (self):
        if (not self.db_enable):
            #skip Db
            return list(self.ORDER_DB.values())
        res_list = self._db_get_all_orders()
        if res_list:
            for order in res_list:
                log.info ("inserting order: %s in cache"%(str(order.id)))
                self.ORDER_DB[order.id] = order          
        return list(self.ORDER_DB.values())
            
    def clear_order_db(self):
        log.info ("clearing order db")
        if (not self.db_enable):
            #skip Db
            return         
        self.ORDER_DB = {}
        self.table.drop(checkfirst=True)
        self.db.session.commit()        

# EOF
