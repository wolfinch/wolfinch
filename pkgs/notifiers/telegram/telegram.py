#! /usr/bin/env python3
'''
# Nasdaq Interface Implementation
# Desc: Implements Telegram Bot interfaces
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

import sys
from decimal import getcontext
import logging
from utils import getLogger #, get_product_config, load_config, get_config
import time
import requests
import urllib

# mpl_logger.setLevel(logging.WARNING)
log = getLogger('Telegram')
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
        log.info("initialized telegram Session")
    log.debug ("get url: %s"%(url))
    r = Session.get(url, timeout=15)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        log.error ("bad response code: %s resp: %s"%(str(r.status_code), r))
        return None
        
class Telegram():
    def __init__(self, bot_token, chat_id=None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        log.info("configured Telgram Notifier instance %s id: %s"%(bot_token, chat_id))
    def send_message (self, msg, chat_id=None):
        log.debug ("msg: %s chat_id: %s"%(msg, chat_id))
        TELEGRAM_SENDMSG_API = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=html' % (
                        self.bot_token, chat_id if chat_id != None else self.chat_id, urllib.parse.quote_plus(msg))
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
            except requests.exceptions.ConnectionError as e:
                log.error("expection while telegram send_msg.  retrying e: %s"%(e))
                time.sleep(2)
                i += 1

######### ******** MAIN ****** #########
if __name__ == '__main__':
    import traceback
    '''
    main entry point
    '''
    getcontext().prec = 8  # decimal precision
    print("Starting Telegram Client..")
    try:
        log.info("Starting Telegram")
        print("Starting Telegram")
        tgram = Telegram("1757210784:AAGXz6sjeBykY-CFCJS-", "785837454")
        status = tgram.send_message("hello there!")
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
    print("\n Telegram Client end")

# EOF
