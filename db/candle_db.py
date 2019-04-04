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
from db import getDb

log = getLogger ('CANDLE-DB')

Db = None

def db_add_or_update_order (market, product_id, order):
    log.debug ("Adding order to db")
    ORDER_DB [uuid.UUID(order.id)] = order
    order.DbSave()
    
    
def db_del_order (market, product_id, order):
    log.debug ("Del order from db")    
    del(ORDER_DB[uuid.UUID(order.id)])
    
    
def db_get_order (OrderCls, market, product_id, order_id):
    log.debug ("Get order from db")    
    order = ORDER_DB.get(uuid.UUID(order_id))  
    if order == None:
        log.info ("order_id:%s not in cache"%(order_id))
        order = OrderCls.DbGet(order_id)
        if order != None:
            ORDER_DB [uuid.UUID(order.id)] = order
        else:
            log.error ("order_id:%s not in Db"%(order_id))
    return order
    
#Get all orders from Db (Should be called part of startup)
def db_get_all_orders(OrderCls):
    global Db
    if not Db:
        Db = getDb()        
        
    try:
        results = Db.session.query(OrderCls).all()
        log.info ("retrieving %d order entries"%(len(results)))
        if results:
            for order in results:
                log.info ("inserting order: %s in cache"%(order.id))
                ORDER_DB[uuid.UUID(order.id)] = order            
            return results
    except Exception, e:
        print(e.message)
    return None
       
# EOF