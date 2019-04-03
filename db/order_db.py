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

from utils import *
from sqlite import SqliteDb

import uuid


log = getLogger ('ORDER-DB')

# Order db is currently a dictionary, keyed with order.id (UUID)
ORDER_DB = {} 

def db_add_or_update_order (exchange, product_id, order):
    log.debug ("Adding order to db")
    ORDER_DB [uuid.UUID(order.id)] = order
def db_del_order (exchange, product_id, order):
    log.debug ("Del order from db")    
    del(ORDER_DB[uuid.UUID(order.id)])
def db_get_order (exchange, product_id, order_id):
    log.debug ("Get order from db")    
    ORDER_DB.get(uuid.UUID(order_id))  
#EOF
