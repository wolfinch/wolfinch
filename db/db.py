#
# wolfinch Auto trading Bot
# Desc: Main File implements Bot
#  Copyright: (c) 2017-2020 Joshith Rayaroth Koderi
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


# use the specific db impl
from .sqlite import SqliteDb

DB = None

def init_db (read_only = False):
    global DB
    if DB == None:
        #use sqlite now
        DB = SqliteDb(read_only)
    return DB
    
def clear_db ():
    global DB
    if DB == None:
        #use sqlite now
        DB = SqliteDb()    
    if DB is not None:
        DB.clear_db()
        
def is_db_enabled():
    import sims  
    if sims.simulator_on:
        return False
    return  True

#EOF
