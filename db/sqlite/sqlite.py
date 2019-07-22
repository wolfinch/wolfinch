#
# OldMonk Auto trading Bot
# Desc: Sqlite db impl
# Copyright 2018, OldMonk. All Rights Reserved.
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
from db import DbBase
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

log = getLogger ('SQLLITE')
log.setLevel (log.CRITICAL)


class SqliteDb (DbBase):    
    def __init__ (self, read_only = False):
        '''
            Db Init
        '''
        def abort_ro(*args, **kwargs):
            # disable flush in readonly
            log.error( "No writing allowed, tsk! ")
            return 
                
        self.engine = db.create_engine('sqlite:///data/OldMonk.sqlite.db', connect_args={'check_same_thread': False})       
#         self.base = declarative_base()
        if self.engine == None :
            log.error ("sqlite or sqlalchemy init failed")
            return None
        else:            
            self.connection = self.engine.connect()
            self.metadata = db.MetaData(bind=self.connection, reflect=True)           
            self.session = sessionmaker(bind=self.engine)()
            
            if read_only == True:
                self.session.flush = abort_ro
                
            if self.connection == None or self.metadata == None or self.session == None:
                log.error ("db connection or metadata init failed")
                return None
            else:
                log.info ("Sqlite Init Done")    
                        
    def clear_db (self):
        
        log.info ("Clear db")
        if (not db):
            return True
        
        log.info ("Clearing all tables")        
        #clear db entries
        self.metadata.drop_all(self.engine)
        self.session.commit()                
        
    def clear_table (self, table_name):
        global client, db    
        if (not db):
            return True    
        log.info ("Clear table: %s"%table_name)                
        table = self.metadata.tables[table_name]
        if table is not None:
            log.info ("Clearing table: %s"%table_name)                            
            table.drop(self.engine)
        
    
    def insert_one (self, entry, table):
        pass
    
    def delete_one (self, entry, table):
        pass
    
    def insert_many (self):
        pass
    
    def delete_many (self):
        pass

#EOF
