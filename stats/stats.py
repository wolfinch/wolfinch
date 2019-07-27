#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Stats implementation for OldMonk Bot
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

import Queue
from   threading import Thread
import time
import pprint
import sys
import os
import sims

from utils import getLogger

log = getLogger ('STATS')
log.setLevel(log.DEBUG)

TRADED_STATS_FILE = "data/stats_traded_orders_%s_%s.json"
POSITION_STATS_FILE = "data/stats_positions_%s_%s.json"
MARKET_STATS_FILE = "data/stats_market_%s_%s.json"
STATS_INTERVAL = 10
_stop = False
g_stats_thread = None

#TODO: FIXME: enhance. This is a super basic impl.
# Dumping the whole order db doesn't scale in long run

# Stats Q routines
statsQ = Queue.Queue()
def _stats_enQ (stats_type, market=None, msg=None):
    obj = (stats_type, market, msg)
    statsQ.put(obj)
    
def _stats_deQ (timeout):
    try:
        if (timeout == 0):
            msg = statsQ.get(False)
        else:
            msg = statsQ.get(block=True, timeout=timeout)
    except Queue.Empty:
        return None
    else:
        return msg

def _stats_run ():
    global STATS_INTERVAL, stop
    while (not _stop):
        msg = _stats_deQ (STATS_INTERVAL)
        if msg != None:
            _process_stats_update(msg)
            
def _process_stats_update(stats_obj):
    stats_type, market, msg = stats_obj[0], stats_obj[1], stats_obj[2]
    if stats_type == "order_book_incr" or stats_type == "order_book_bulk" :
            with open(MARKET_STATS_FILE%(market.exchange_name, market.product_id), "w") as fd:
                st = str(market)
                fd.write(st)              
            #with open(POSITION_STATS_FILE%(market.exchange_name, market.product_id), "w") as fd:
            #    market.order_book.dump_positions(fd)         
    
######### ******** MAIN ****** #########
                
def stats_update_order(market, order):
    if not sims.backtesting_on:
        _stats_enQ("order_book_incr", market, order)

def stats_update_order_bulk(market):
    if not sims.backtesting_on:
        _stats_enQ("order_book_bulk", market)    
    
def clear_stats():
    os.system("rm -rf data/stats_*")
    
def start ():
    global g_stats_thread
    if not sims.backtesting_on:    
        g_stats_thread = Thread(target=_stats_run)
        g_stats_thread.start()
    
def stop ():
    global _stop, g_stats_thread
    _stop = True
    if g_stats_thread:
        g_stats_thread.join()

#EOF
