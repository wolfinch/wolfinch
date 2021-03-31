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

from .telegram import Telegram

telegram = None
def Configure(cfg):
    global telegram
    tgram = cfg.get("telegram")
    if tgram:
        telegram = Telegram(tgram["token"], tgram["chat-id"])
    
def notify(msg):
    if telegram:
        telegram.send_message(msg)
# EOF