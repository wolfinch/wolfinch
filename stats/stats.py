#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Stats implementation for OldMonk Bot
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

import Queue
from   threading import Thread
import time
import pprint
import sys
import os

from utils import getLogger

log = getLogger ('STATS')
log.setLevel(log.DEBUG)

TRADED_STATS_FILE = "data/stats_traded_orders_%s_%s.json"
MARKET_STATS_FILE = "data/stats_market_%s_%s.json"
STATS_INTERVAL = 10
_stop = False

#TODO: FIXME: enhance. This is a super basic impl.
# Dumping the whole order db doesn't scale in long run

# Stats Q routines
statsQ = Queue.Queue()
def _stats_enQ (market, msg):
    obj = {"market":market, "msg":msg}
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
            m = msg['market']
            with open(MARKET_STATS_FILE%(m.exchange_name, m.product_id), "w") as fd:
                st = str(m)
                fd.write(st)              
            with open(TRADED_STATS_FILE%(m.exchange_name, m.product_id), "w") as fd:
                m.order_book.dump_traded_orders(fd)            
                
######### ******** MAIN ****** #########
                
def stats_update(market, order):
    _stats_enQ(market, order)

def start ():
    t = Thread(target=_stats_run)
    t.start()
    
def stop ():
    global _stop
    _stop = True
    

#EOF
