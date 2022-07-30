#! /usr/bin/env python3
'''
# 
# Desc: Implements Twitter interfaces
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

import sys
from decimal import getcontext
import logging
from utils import getLogger #, get_product_config, load_config, get_config
import time
import requests
import urllib

# mpl_logger.setLevel(logging.WARNING)
log = getLogger('Twitter')
log.setLevel(log.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)

Session = None
def get_url(url):
    global Session
    if Session == None:
        Session = requests.session()
#         headers = {
#             "Accept": "application/json, text/plain, */*",
#             "Accept-Encoding": "gzip, deflate",
#             "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",  # noqa: E501
#             "Connection": "keep-alive",
#         }
#         Session.headers = headers
        log.info("initialized twitter Session")
    log.debug ("get url: %s"%(url))
    r = Session.get(url, timeout=15)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        log.error ("bad response code: %s resp: %s"%(str(r.status_code), r))
        return None
        
class Notifier():
    def __init__(self, token=None, chat_id=None, **kwarg):
        self.bot_token = token
        self.chat_id = chat_id
        self.msg_l = {}
        self.msg_len = 0
        log.info("configured Telgram Notifier instance %s id: %s"%(token, chat_id))
    def send_message (self, name, msg, chat_id=None):
        log.debug ("msg: %s chat_id: %s"%(msg, chat_id))
        
        if name:
            if not self.msg_l.get(name):
                self.msg_l[name] = []
            self.msg_l[name].append (msg)
            self.msg_len += 1
        if self.msg_len > 0 and (self.msg_len > 25 or not name):
            log.info("notify msg len: %d"%(self.msg_len))
            self._send_msg(self.msg_l)
            self.msg_l = {}
            self.msg_len = 0
    def _fmt_msg (self, msg_l):
        msg_str = ""
        for k, v_l in msg_l.items():
            v_str = ""
            for v in v_l:
                v_str = v_str + str(v) + "\n"
            msg_str = msg_str+"<b>"+k+":</b>" + str(v_str)
        return msg_str
    def _send_msg(self, msg_l, chat_id=None):
        msg_str = self._fmt_msg(msg_l)
        TELEGRAM_SENDMSG_API = 'https://api.twitter.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=html' % (
                        self.bot_token, chat_id if chat_id != None else self.chat_id, urllib.parse.quote_plus(msg_str))
        i = 0
        while i < 2:
            try:
                data = get_url (TELEGRAM_SENDMSG_API)
                if data:
                    log.debug("send msg success %s"%(data))
                    return True
                else:
                    log.error("failed ")
                    return False
            except Exception as e:
                log.error("expection while twitter send_msg.  retrying e: %s"%(e))
                time.sleep(2)
                i += 1        
######### ******** MAIN ****** #########
if __name__ == '__main__':
    import traceback
    '''
    main entry point
    '''
    getcontext().prec = 8  # decimal precision
    print("Starting Twitter Client..")
    try:
        log.info("Starting Twitter")
        print("Starting Twitter")
        twit = Twitter("1757210784:AAGXz6sjeBykY-CFCJS-", "785837454")
        status = twit.send_message("hello there!")
        print ("send msg status: %s"%(status))
    except(KeyboardInterrupt, SystemExit):
        sys.exit()
    except Exception as e:
        log.critical("Unexpected error: exception: %s" %(traceback.format_exc()))
        print("Unexpected error: exception: %s" %(traceback.format_exc()))
        raise
#         traceback.print_exc()
#         os.abort()
    # '''Not supposed to reach here'''
    print("\n Twitter Client end")

# EOF
