from utils import *
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