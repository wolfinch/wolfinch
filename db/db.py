'''
 OldMonk Auto trading Bot
 Desc: highlevel Db Implementation
 (c) Joshith Rayaroth Koderi
'''

# use the specific db impl
from sqlite import SqliteDb

DB = None

def init_db ():
    global DB
    if DB == None:
        #use sqlite now
        DB = SqliteDb()
    return DB
    
def clear_db ():
    global DB
    if DB == None:
        #use sqlite now
        DB = SqliteDb()    
    if DB is not None:
        DB.clear_db()
#EOF
