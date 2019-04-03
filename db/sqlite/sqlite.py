from utils import *
from db_base import DB
import sqlalchemy as db

log = getLogger ('SQLLITE')


class SqliteDb (DB):    
    def __init__ (self):
        '''
            Db Init
        '''
        self.engine = db.create_engine('sqlite:///data/OldMonk.sqlite.db')       
        
        if self.engine == None :
            log.error ("sqlite or sqlalchemy init failed")
            return False
        else:
            log.info ("Sqlite Init Done")
            
            self.connection = self.engine.connect()
            self.metadata = db.MetaData()             
            if self.connection == None or self.metadata == None:
                log.error ("db connection or metadata init failed")
                return False
                
            return True
        
    def clear_db ():
        global client, db    
        if (not db):
            return True
        
        #clear db entries
        client.drop_database("OldMonkDb")
        
    def clear_table (table):
        global client, db    
        if (not db):
            return True    
        db.drop_collection (table)
        
    
    def insert_one (entry, table):
        pass
    
    def delete_one (entry, table):
        pass
    
    def insert_many ():
        pass
    
    def delete_many ():
        pass

#EOF
