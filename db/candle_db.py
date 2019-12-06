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
from .db import init_db
from sqlalchemy import *
from sqlalchemy.orm import mapper 

log = getLogger ('CANDLE-DB')
log.setLevel (log.CRITICAL)

class CandlesDb(object):
    def __init__ (self, ohlcCls, exchange_name, product_id, read_only=False):
        self.OHLCCls = ohlcCls
        self.db = init_db(read_only)
        log.info ("init candlesdb")
        self.table_name = "candle_%s_%s"%(exchange_name, product_id)
        if not self.db.engine.dialect.has_table(self.db.engine, self.table_name):  # If table don't exist, Create.
            # Create a table with the appropriate Columns
            log.info ("creating table: %s"%(self.table_name))            
            self.table = Table(self.table_name, self.db.metadata,
#                 Column('Id', Integer, primary_key=True),
#                 Column('time', Integer, nullable=False),
                Column('time', Integer, primary_key=True, nullable=False),                
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
        
    def db_get_candles_after_time(self, after):
        log.debug ("retrieving candles after time: %d from db"%(after))
        try:
            res_list = []            
            ResultSet = self.db.session.query(self.mapping).filter(self.ohlcCls.time >= after).order_by(self.ohlcCls.time).all()
            log.info ("Retrieved %d candles for table: %s"%(len(ResultSet), self.table_name))
            
            if (len(ResultSet)):
                res_list = [self.OHLCCls(c.time, c.open, c.high, c.low, c.close, c.volume) for c in ResultSet]
            #clear cache now
            self.db.session.expire_all()
            return res_list
        except Exception as e:
            print(e.message)          
        
        
    def db_get_all_candles (self):
        log.debug ("retrieving candles from db")
        try:
#             query = select([self.table])
#             ResultProxy = self.db.connection.execute(query)
#             ResultSet = ResultProxy.fetchall()
            ResultSet = self.db.session.query(self.mapping).order_by(self.ohlcCls.time).all()
            log.info ("Retrieved %d candles for table: %s"%(len(ResultSet), self.table_name))
            
            if (len(ResultSet)):
                res_list = [self.OHLCCls(c.time, c.open, c.high, c.low, c.close, c.volume) for c in ResultSet]
            #clear cache now
            self.db.session.expire_all()
            return res_list
        except Exception as e:
            print(e.message)        
   
# EOF
