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
    
    cdl_db = db.CandlesDb(OHLC, EXCH_NAME, PRODUCT_ID)
    order_db = db.OrderDb(Order, EXCH_NAME, PRODUCT_ID)
    position_db = db.PositionDb(Position, EXCH_NAME, PRODUCT_ID)



def get_all_candles():
    
    log.debug("ENTER")
    return cdl_db.db_get_all_candles()

#EOF
