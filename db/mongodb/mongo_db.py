from utils import *
from pymongo import MongoClient
from db import DbBase

log = getLogger ('MONGO')
client = None
db = None

class MongoDb (DbBase):
    def __init__ (self):
        '''
            Db Init
        '''
        global client, db
        client = MongoClient()
    #     client = MongoClient('localhost', 27017)
        if client == None:
            log.error ("MongoDb init failed")
            return False
        else:
            log.info ("MongoDb Init Done")
            db = client['OldMonkDb']
            return True
        
    def clear_db (self):
        global client, db    
        if (not db):
            return True
        
        #clear db entries
        client.drop_database("OldMonkDb")
        
    def clear_table (self, table):
        global client, db    
        if (not db):
            return True    
        db.drop_collection (table)
        
    
    def insert_one (self, entry, table):
        pass
    
    def delete_one (self, entry, table):
        pass
    
    def insert_many (self):
        pass
    
    def delete_many (self):
        pass

#EOF
