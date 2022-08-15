#! /usr/bin/env python3
'''
# Nasdaq Interface Implementation
# Desc: Implements Notifier interfaces
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
'''
import threading
import queue
import notifiers.telegram as t
import notifiers.twitter as ti
import notifiers.wolfinch as w
import time

msg_queue = None
stop = False
MAIN_TICK_DELAY = 1.000
notifiers = {}
def configure(cfg):
    global notifiers
    for k, v in cfg.items():
        try:
            if k == "enabled":
                continue
            elif k == "telegram":
                no = t.Notifier(**v)
            elif k == "twitter":
                no = ti.Notifier(**v)                
            elif k == "wolfinch":
                no = w.Notifier(**v)
            else:
                print ("unknown notifier %s"%(k))
                return False
            notifiers[k] = no
        except Exception as e:
            print ("excpetion while configuring notifier \n %s"%(e))
            raise e
    return True
def notify(kind, name, msg):
    if msg_queue:
        msg_queue.put((kind, name, msg))
def _send_msg(kind, name, data):
    global notifiers
    if kind == None or kind == "all":
        for _, v in notifiers.items():
            v.send_message(name, data)
    else:
        v = notifiers.get(kind)
        if v:
            v.send_message(name, data)
def _notifier_loop():
    sleep_time = MAIN_TICK_DELAY
    while not stop:
        try:
            cur_time = time.time()
            msg = msg_queue.get(timeout=sleep_time)
            kind = msg[0]
            name = msg[1]
            data = msg[2]
            _send_msg(kind, name, data)
            sleep_time = (MAIN_TICK_DELAY -(time.time()-cur_time))
            sleep_time = 0 if sleep_time < 0 else sleep_time
        except queue.Empty:
            _send_msg(None, None, None)
            sleep_time = MAIN_TICK_DELAY
def init(cfg):
    global notify_thread, msg_queue
    if cfg == None or cfg.get("enabled") == None or cfg.get("enabled") == False:
        #notifier not configured, nothing to do
        return True
    if False == configure(cfg):
        return False
    msg_queue = queue.Queue()
    notify_thread = threading.Thread(target=_notifier_loop)
    notify_thread.daemon = True
    notify_thread.start()
    return True
def end():
    global stop
    stop = True
def is_notify_enabled():
    return notify_thread != None
# EOF