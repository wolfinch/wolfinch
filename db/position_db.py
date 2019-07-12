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

log = getLogger ('POSITION-DB')
log.setLevel (log.CRITICAL)

class PositionDb(object):
    def __init__ (self, positionCls, exchange_name, product_id):
#         self.positionCls = positionCls
        self.db = init_db()
        log.info ("init positionsdb")
        self.table_name = "position_%s_%s"%(exchange_name, product_id)
        if not self.db.engine.dialect.has_table(self.db.engine, self.table_name):  # If table don't exist, Create.
            # Create a table with the appropriate Columns
            log.info ("creating table: %s"%(self.table_name))
            self.table = Table(self.table_name, self.db.metadata,   
                Column('id', String(64), index=True, nullable=False, primary_key=True),
                Column('buy', String(64), index=True, nullable=False),
                Column('sell', String(64), index=True, nullable=False),
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
                    self.buy = c.buy.id  if c.buy else ''
                    self.sell = c.sell.id if c.sell else ''
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
#         self.db.connection.execute(self.table.insert(), {'close':position.close, 'high':position.high,
#                                                               'low':position.low, 'open':position.open, 
#                                                               'time':position.time, 'volume':position.volume})
        c = self.positionCls(position)
        self.db.session.merge (c)
        self.db.session.commit()
        
    def db_save_positions (self, positions):
        log.debug ("Adding position list to db")
#         self.db.connection.execute(self.table.insert(), map(lambda cdl: 
#                                                             {'close':cdl.close, 'high':cdl.high,
#                                                               'low':cdl.low, 'open':cdl.open, 
#                                                               'time':cdl.time, 'volume':cdl.volume}, positions))
#         cdl_list = map(lambda cdl: 
#                                         {'close':cdl.close, 'high':cdl.high,
#                                             'low':cdl.low, 'open':cdl.open, 
#                                             'time':cdl.time, 'volume':cdl.volume}, positions)
        for cdl in positions:
            c = self.positionCls(cdl)
            self.db.session.merge (c)
        self.db.session.commit()
        
    def db_delete_positiono(self, position):
        c = self.positionCls(position)
        self.db.session.delete (c)
        self.db.session.commit()        
        
        
    def db_get_all_positions (self):
        log.debug ("retrieving positions from db")
        try:
#             query = select([self.table])
#             ResultProxy = self.db.connection.execute(query)
#             ResultSet = ResultProxy.fetchall()
            ResultSet = self.db.session.query(self.mapping).order_by(self.positionCls.time).all()
            log.info ("Retrieved %d positions for table: %s"%(len(ResultSet), self.table_name))
#             log.debug ("Res: %s"%str(ResultSet))
            return ResultSet
        except Exception, e:
            print(e.message)        
   
# EOF