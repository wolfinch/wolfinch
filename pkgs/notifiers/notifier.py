#! /usr/bin/env python3
'''
# Nasdaq Interface Implementation
# Desc: Implements Notifier interfaces
#  Copyright: (c) 2017-2021 Joshith Rayaroth Koderi
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
from .telegram import Telegram
from .wolfinch import Wolfinch
import time

telegram = None
wolfinch = None
msg_queue = None
stop = False
MAIN_TICK_DELAY = 1.000
def configure(cfg):
    global telegram, wolfinch
    for k, v in cfg.items():
        if k == "telegram":
            telegram = Telegram(v["token"], v["chat-id"])
        elif k == "wolfinch":
            wolfinch = Wolfinch(v["bot"], v["exchange"], v["secret"])
        else:
            print ("unknown notifier %s"%(k))
            return False
    return True
def notify(kind, name, msg):
    if msg_queue:
        msg_queue.put((kind, name, msg))
def _send_msg(msg_l):
    msg_str = ""
    for k, v_l in msg_l.items():
        v_str = ""
        for v in v_l:
            v_str = v_str + str(v) + "\n"
        msg_str = msg_str+"<b>"+k+":</b>" + str(v_str)
    if telegram:
        telegram.send_message(msg_str)
def _notifier_loop():
    msg_l = {}
    msg_len = 0
    sleep_time = MAIN_TICK_DELAY
    while not stop:
        try:
            cur_time = time.time()
            msg = msg_queue.get(timeout=sleep_time)
            kind = msg[0]
            name = msg[1]
            data = msg[2]
            if kind == "telegram":
                if not msg_l.get(name):
                    msg_l[name] = []
                msg_l[name].append (data)
                msg_len += 1
                if msg_len > 25:
                    _send_msg(msg_l)
                    msg_l = {}
                    msg_len = 0
            else:
                print("unknown notify type %s"%(kind))
            sleep_time = (MAIN_TICK_DELAY -(time.time()-cur_time))
            sleep_time = 0 if sleep_time < 0 else sleep_time
        except queue.Empty:
            if msg_len:
                _send_msg(msg_l)
                msg_l = {}
                msg_len = 0
            sleep_time = MAIN_TICK_DELAY
def init(cfg):
    global notify_thread, msg_queue
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
# EOF