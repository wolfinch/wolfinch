#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Main File implements Bot
# Copyright 2018, OldMonk Bot. All Rights Reserved.
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

from __future__ import print_function
import time
import pkgutil
import pprint
import sys
from decimal import *
import argparse
import os

import json
import db
from market import Position, OHLC, Order

from utils import getLogger
from utils.readconf import readConf
from dateparser import conf

log = getLogger ('UI-DB')
log.setLevel(log.DEBUG)

EXCH_NAME = "CBPRO"
PRODUCT_ID = "BTC-USD"

cdl_db, order_db, position_db = None, None, None


def init ():
    global cdl_db, order_db, position_db
    
    cdl_db = db.CandlesDb(OHLC, EXCH_NAME, PRODUCT_ID, read_only=True)
    order_db = db.OrderDb(Order, EXCH_NAME, PRODUCT_ID, read_only=True)
    position_db = db.PositionDb(Position, EXCH_NAME, PRODUCT_ID, read_only=True)

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
