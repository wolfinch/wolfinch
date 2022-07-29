#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: UI db ops impl
#  Copyright: (c) 2017-2022 Wolfinch Inc.
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


import time
import db
from market import Position, OHLC, Order
from utils import getLogger

log = getLogger ('UI-DB')
log.setLevel(log.DEBUG)

cdl_db, order_db, position_db = None, None, None


def init (exch_name, prod_id):
    global cdl_db, order_db, position_db
    
    cdl_db = db.CandlesDb(OHLC, exch_name, prod_id, read_only=True)
    order_db = db.OrderDb(Order, exch_name, prod_id, read_only=True)
    position_db = db.PositionDb(Position, exch_name, prod_id, read_only=True)

    if not (cdl_db and position_db and order_db):
        log.error ("db init failed")
        return False
    
    log.info ("db_events init success")
    return True 

def get_all_candles(period=1):
    
    log.debug("ENTER ")
    
    #time calc - cur_time - sec in perd
    after = int(time.time()) - period * 60 * 60 * 24
    
    log.debug ("period: %d cdl_first_time: %d"%(period, after))
    
    cdl_li = cdl_db.db_get_candles_after_time(after)
    if cdl_li:
        log.info ("got (%d) candles"%(len(cdl_li)))
        cdl_s = str(cdl_li)
        return cdl_s
    else:
        log.error ("unable to get candles")
        return "[]"

def get_all_positions():
    log.debug ("ENTER")
    
    pos_li = position_db.db_get_all_positions(order_db)
    
    if pos_li:
        log.info ("got (%d) positions"%(len(pos_li)))
        pos_s = str(pos_li)
        return pos_s
    else:
        log.error ("unable to get positions")
        return "[]"
#EOF
