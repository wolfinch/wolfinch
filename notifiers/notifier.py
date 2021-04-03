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
import time

telegram = None
msg_queue = None
stop = False
MAIN_TICK_DELAY = 1.000
def configure(cfg):
    global telegram
    tgram = cfg.get("telegram")
    if tgram:
        telegram = Telegram(tgram["token"], tgram["chat-id"])
        return True
    else:
        return False
def notify(msg):
    if msg_queue:
        msg_queue.put(msg)
def _send_msg(msg_l):
    msg_str = ""
    for msg in msg_l:
        msg_str = msg_str + str(msg) + "\n"
    if telegram:
        telegram.send_message(msg_str)
def _notifier_loop():
    msg_l = []
    sleep_time = MAIN_TICK_DELAY
    while not stop:
        try:
            cur_time = time.time()
            msg_l.append (msg_queue.get(timeout=sleep_time))
            if len(msg_l) > 25:
                _send_msg(msg_l)
                msg_l = []          
            sleep_time = (MAIN_TICK_DELAY -(time.time()-cur_time))
            sleep_time = 0 if sleep_time < 0 else sleep_time
        except queue.Empty:
            if len(msg_l):
                _send_msg(msg_l)
                msg_l = []
            sleep_time = MAIN_TICK_DELAY
def init(cfg):
    global notify_thread, msg_queue
    if False == configure(cfg):
        return 
    msg_queue = queue.Queue()
    notify_thread = threading.Thread(target=_notifier_loop)
    notify_thread.daemon = True
    notify_thread.start()
def end():
    global stop
    stop = True
# EOF