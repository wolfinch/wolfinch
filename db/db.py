#
# OldMonk Auto trading Bot
# Desc: Main File implements Bot
# Copyright 2017-2019, Joshith Rayaroth Koderi. All Rights Reserved.
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


# use the specific db impl
from sqlite import SqliteDb

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
    import sims, ui    
    if sims.simulator_on and not ui.integrated_ui:
        return False
    return  True

#EOF
