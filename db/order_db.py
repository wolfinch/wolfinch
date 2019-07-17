#
# OldMonk Auto trading Bot
# Desc: order_db impl
# Copyright 2018, OldMonk Bot. All Rights Reserved.
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

from utils import getLogger
from db import init_db
import sims
from sqlalchemy import *
from sqlalchemy.orm import mapper 
# import sys

import uuid

log = getLogger ('ORDER-DB')
log.setLevel (log.DEBUG)

# Order db is currently a dictionary, keyed with order.id (UUID)

class OrderDb(object):
    def __init__ (self, orderCls, market):
#         self.orderCls = orderCls

        self.ORDER_DB = {}
        
        if (sims.simulator_on):
            # skip db init
            log.info ("sim on, skip db init")
            return    
        
        self.db = init_db()
        self.market = market
        self.exchange_name = market.exchange_name
        self.product_id = market.product_id
        
        log.info ("init ordersdb")
        self.table_name = "order_%s_%s"%(self.exchange_name, self.product_id)
        if not self.db.engine.dialect.has_table(self.db.engine, self.table_name):  # If table don't exist, Create.
            # Create a table with the appropriate Columns
            log.info ("creating table: %s"%(self.table_name))
            self.table = Table(self.table_name, self.db.metadata,   
                Column('id', String(64), index=True, nullable=False, primary_key=True),
                Column('product_id', String(64), index=True, nullable=False),
                Column('order_type', String(64), index=True, nullable=True),
                Column('status_type', String(64), index=True, nullable=True),
                Column('status_reason', String(64), index=True, nullable=True),   
                Column('side', String(64), index=True, nullable=False),
                Column('request_size', Numeric, default=0),
                Column('filled_size', Numeric, default=0),
                Column('remaining_size', Numeric, default=0),    
                Column('price', Numeric, default=0),
                Column('funds', Numeric, default=0),
                Column('fees', Numeric, default=0),                   
                Column('create_time', String(64), nullable=True),
                Column('update_time', String(64)))
            # Implement the creation
            self.db.metadata.create_all(self.db.engine, checkfirst=True)   
        else:
            log.info ("table %s exists already"%self.table_name)
            self.table = self.db.metadata.tables[self.table_name]
        try:
            # HACK ALERT: to support multi-table with same class on sqlalchemy mapping
            class T (orderCls):
                def __init__ (self, c):
                    self.id = c.id
                    self.product_id = c.product_id
                    self.order_type = c.order_type
                    self.status_type = c.status_type
                    self.status_reason = c.status_reason
                    self.side = c.side
                    self.request_size = c.request_size                    
                    self.filled_size = c.filled_size
                    self.remaining_size = c.remaining_size
                    self.price = c.price
                    self.funds = c.funds
                    self.fees = c.fees                    
                    self.create_time = c.create_time
                    self.update_time = c.update_time                                  
            self.orderCls = T
            self.mapping = mapper(self.orderCls, self.table)
            
            log.debug ("retrieve order list from db")
            results = self.db.session.query(self.orderCls).all()
            log.info ("retrieving %d order entries"%(len(results)))
            if results:
                for order in results:
                    log.info ("inserting order: %s in cache"%(order.id))
                    self.ORDER_DB[uuid.UUID(order.id)] = order
    #             sys.exit()
        except Exception as e:
            log.debug ("mapping failed with except: %s \n trying once again with non_primary mapping"%(e))
            raise e
                    
    def __str__ (self):
        return "****** Not-Implemented ******"
    
    def _db_save_order (self, order):
        log.debug ("Adding order to db")

        c = self.orderCls(order)
        self.db.session.merge (c)
        self.db.session.commit()
        
    def _db_save_orders (self, orders):
        log.debug ("Adding order list to db")

        for cdl in orders:
            c = self.orderCls(cdl)
            self.db.session.merge (c)
        self.db.session.commit()
        
    def _db_delete_order(self, order):
        c = self.orderCls(order)
        self.db.session.delete (c)
        self.db.session.commit()
        
    def _db_get_all_orders (self):
        log.debug ("retrieving orders from db")
        try:
            ResultSet = self.db.session.query(self.mapping).all()
            log.info ("Retrieved %d orders for table: %s"%(len(ResultSet), self.table_name))
#             log.debug ("Res: %s"%str(ResultSet))
            if not ResultSet:
                return None
            return ResultSet
        except Exception, e:
            log.critical(e.message)
# EOF

    def db_add_or_update_order (self, order):
        log.debug ("Adding order to db")
        self.ORDER_DB [uuid.UUID(order.id)] = order
        
    #     if not ( sims.backtesting_on or sims.simulator_on):
        if not (sims.simulator_on):
            self._db_save_order(order)
        
        
    def db_del_order (self, order):
        log.debug ("Del order from db")    
        del(self.ORDER_DB[uuid.UUID(order.id)])
        #TODO: FIXME: Handle Db here ??
         
        if not (sims.simulator_on):        
            self._db_delete_order(order)
        
    def db_get_order (self, order_id):
        log.debug ("Get order from db")
        order = self.ORDER_DB.get(uuid.UUID(order_id))  
        
        if (sims.simulator_on):        
            #skip Db
            return order
        
        if order == None:
            log.info ("order_id:%s not in cache"%(order_id))
            try:
                result = self.db.session.query(self.mapping).filter_by(id=order_id)
                if result:
                    log.info ("get order from db")                
                    order = result.first()
                if order != None:
                    self.ORDER_DB [uuid.UUID(order.id)] = order
                else:
                    log.error ("order_id:%s not in Db"%(order_id))                    
            except Exception, e:
                print(e.message)

        return order
        
    def get_all_orders (self):
        return self.ORDER_DB.values()
            
#     #Get all orders from Db (Should be called part of startup)
#     def init_order_db(OrderCls):
#         global Db
#         
#     #     if ( sims.backtesting_on or sims.simulator_on):    
#         if (sims.simulator_on):
#             #don't do order db init for sim
#             return None
#          
#         if not Db:
#             Db = init_db()
#             if not Db:
#                 log.critical ("Unable to get Db instance")
#                 return None
#             log.info ("init order_db table")
#             OrderCls.DbCreateTable()
#         try:
#             log.debug ("retrieve order list from db")
#             results = Db.session.query(OrderCls).all()
#             log.info ("retrieving %d order entries"%(len(results)))
#             if results:
#                 for order in results:
#                     log.info ("inserting order: %s in cache"%(order.id))
#                     self.ORDER_DB[uuid.UUID(order.id)] = order
#     #             sys.exit()
#                 return results
#         except Exception, e:
#             print(e.message)
#         return None
#     def clear_order_db (self, OrderCls):
#         global Db
#         if not Db:
#             Db = init_db()
#             if not Db:
#                 log.critical ("Unable to get Db instance")
#                 return None
#         try:
#             log.info ("clear order_db table")
#             OrderCls.DbDropTable()
#         except Exception, e:
#             print(e.message)
#         return None    
           

# EOF