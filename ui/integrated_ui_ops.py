#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: integrated UI impl.
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
from multiprocessing import Process, Pipe

from utils import getLogger

import ui_server

log = getLogger ('UI-OPS')
log.setLevel(log.DEBUG)

g_p = None

def ui_mp_init ():
    global g_p
    
    log.info ("init multi-process ui")
    
    parent_conn, child_conn = Pipe()
    
    g_p = Process(target=ui_server.ui_main, args=(child_conn,))
    g_p.start()
    
    return parent_conn
    
def ui_mp_end ():
    
    log.info ("finishing ui")
    
    if g_p == None:
        return
    
    g_p.terminate()
    g_p.join()
    
#EOF
