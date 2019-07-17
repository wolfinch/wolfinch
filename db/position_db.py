#
# OldMonk Auto trading Bot
# Desc: Position impl
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
from sqlalchemy import *
from sqlalchemy.orm import mapper 
import order_db

log = getLogger ('POSITION-DB')
log.setLevel (log.CRITICAL)

class PositionDb(object):
    def __init__ (self, positionCls, market):
#         self.positionCls = positionCls
        self.db = init_db()
        self.market = market
        self.exchange_name = market.exchange_name
        self.product_id = market.product_id
        
        log.info ("init positionsdb")
        self.table_name = "position_%s_%s"%(self.exchange_name, self.product_id)
        if not self.db.engine.dialect.has_table(self.db.engine, self.table_name):  # If table don't exist, Create.
            # Create a table with the appropriate Columns
            log.info ("creating table: %s"%(self.table_name))
            self.table = Table(self.table_name, self.db.metadata,   
                Column('id', String(64), index=True, nullable=False, primary_key=True),
                Column('buy', String(64), index=True, nullable=False),
                Column('sell', String(64), index=True, nullable=True),
                Column('profit', Numeric, default=0),
                Column('stop_loss', Numeric, default=0),
                Column('take_profit', Numeric, default=0),    
                Column('status', String(64), nullable=False),
                Column('open_time', String(64)),
                Column('closed_time', String(64)))
            
            # Implement the creation
            self.db.metadata.create_all(self.db.engine, checkfirst=True)   
        else:
            log.info ("table %s exists already"%self.table_name)
            self.table = self.db.metadata.tables[self.table_name]
        try:
            # HACK ALERT: to support multi-table with same class on sqlalchemy mapping
            class T (positionCls):
                def __init__ (self, c):
                    self.id = c.id
                    self.buy = c.buy.id  if c.buy else None
                    self.sell = c.sell.id if c.sell else None
                    self.profit = c.profit
                    self.stop_loss = c.stop_loss
                    self.take_profit = c.take_profit
                    self.status = c.status                    
                    self.open_time = c.open_time
                    self.closed_time = c.closed_time                      
            self.positionCls = T
            self.mapping = mapper(self.positionCls, self.table)
        except Exception as e:
            log.debug ("mapping failed with except: %s \n trying once again with non_primary mapping"%(e))
            raise e
                    
    def __str__ (self):
        return "{id: %s, buy: %g, sell: %g, profit: %g, stop_loss: %g, take_profit: %g, status: %g, open_time: %s, closed_time: %s}"%(
            self.id, self.buy, self.sell, self.profit, self.stop_loss, self.take_profit, self.status, self.open_time, self.closed_time)


    def db_save_position (self, position):
        log.debug ("Adding position to db")

        c = self.positionCls(position)
        self.db.session.merge (c)
        self.db.session.commit()
        
    def db_save_positions (self, positions):
        log.debug ("Adding position list to db")

        for cdl in positions:
            c = self.positionCls(cdl)
            self.db.session.merge (c)
        self.db.session.commit()
        
    def db_delete_position(self, position):
        c = self.positionCls(position)
        self.db.session.delete (c)
        self.db.session.commit()        
        
        
    def db_get_all_positions (self, OrderCls):
        log.debug ("retrieving positions from db")
        try:
            ResultSet = self.db.session.query(self.mapping).all()
            log.info ("Retrieved %d positions for table: %s"%(len(ResultSet), self.table_name))
#             log.debug ("Res: %s"%str(ResultSet))
            if not ResultSet:
                return None
            for pos in ResultSet:
                if pos.buy == null or pos.buy == '':
                    pos.buy = None
                if pos.sell == null or pos.sell == '':
                    pos.sell = None                    
                if pos.buy:
                    pos.buy = order_db.db_get_order(OrderCls, self.market, self.product_id, pos.buy)
                if pos.sell:
                    pos.sell = order_db.db_get_order(OrderCls, self.market, self.product_id, pos.sell)
            return ResultSet
        except Exception, e:
            log.critical(e.message)        
   
# EOF