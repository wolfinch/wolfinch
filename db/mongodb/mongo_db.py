from utils import *
from pymongo import MongoClient

log = getLogger ('MONGO')
client = None
db = None

def init ():
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
