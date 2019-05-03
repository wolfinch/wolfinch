#
# OldMonk Auto trading Bot
# Desc: order_db impl
# Copyright 2018, Joshith Rayaroth Koderi. All Rights Reserved.
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

log = getLogger ('CANDLE-DB')


class CandlesDb(object):
    def __init__ (self, ohlcCls, exchange_name, product_id):
#         self.ohlcCls = ohlcCls
        self.db = init_db()
        log.info ("init candlesdb")
        self.table_name = "candle_%s_%s"%(exchange_name, product_id)
        if not self.db.engine.dialect.has_table(self.db.engine, self.table_name):  # If table don't exist, Create.
            # Create a table with the appropriate Columns
            log.info ("creating table: %s"%(self.table_name))            
            self.table = Table(self.table_name, self.db.metadata,
                Column('Id', Integer, primary_key=True),
                Column('time', Integer, nullable=False),
#                 Column('time', Integer, primary_key=True, nullable=False),                
                Column('open', Numeric, default=0),
                Column('high', Numeric, default=0),
                Column('low', Numeric, default=0),
                Column('close', Numeric, default=0),
                Column('volume', Numeric, default=0))
            # Implement the creation
            self.db.metadata.create_all(self.db.engine, checkfirst=True)   
        else:
            log.info ("table %s exists already"%self.table_name)
            self.table = self.db.metadata.tables[self.table_name]
        try:
            # HACK ALERT: to support multi-table with same class on sqlalchemy mapping
            class T (ohlcCls):
                def __init__ (self, c):
                    self.time = c.time
                    self.open = c.open
                    self.high = c.high
                    self.low = c.low
                    self.close = c.close
                    self.volume = c.volume
            self.ohlcCls = T
            self.mapping = mapper(self.ohlcCls, self.table)
        except Exception as e:
            log.debug ("mapping failed with except: %s \n trying once again with non_primary mapping"%(e))
#             self.mapping = mapper(ohlcCls, self.table, non_primary=True)            
            raise e
                    
    def __str__ (self):
        return "{time: %s, open: %g, high: %g, low: %g, close: %g, volume: %g}"%(
            str(self.time), self.open, self.high, self.low, self.close, self.volume)


    def db_save_candle (self, candle):
        log.debug ("Adding candle to db")
#         self.db.connection.execute(self.table.insert(), {'close':candle.close, 'high':candle.high,
#                                                               'low':candle.low, 'open':candle.open, 
#                                                               'time':candle.time, 'volume':candle.volume})
        c = self.ohlcCls(candle)
        self.db.session.merge (c)
        self.db.session.commit()
        
    def db_save_candles (self, candles):
        log.debug ("Adding candle list to db")
#         self.db.connection.execute(self.table.insert(), map(lambda cdl: 
#                                                             {'close':cdl.close, 'high':cdl.high,
#                                                               'low':cdl.low, 'open':cdl.open, 
#                                                               'time':cdl.time, 'volume':cdl.volume}, candles))
#         cdl_list = map(lambda cdl: 
#                                         {'close':cdl.close, 'high':cdl.high,
#                                             'low':cdl.low, 'open':cdl.open, 
#                                             'time':cdl.time, 'volume':cdl.volume}, candles)
        for cdl in candles:
            c = self.ohlcCls(cdl)
            self.db.session.merge (c)
        self.db.session.commit()
        
    def db_get_all_candles (self):
        log.debug ("retrieving candles from db")
        try:
#             query = select([self.table])
#             ResultProxy = self.db.connection.execute(query)
#             ResultSet = ResultProxy.fetchall()
            ResultSet = self.db.session.query(self.mapping).order_by(self.ohlcCls.time).all()
            log.info ("Retrieved %d candles for table: %s"%(len(ResultSet), self.table_name))
#             log.debug ("Res: %s"%str(ResultSet))
            return ResultSet
        except Exception, e:
            print(e.message)        
   
# EOF