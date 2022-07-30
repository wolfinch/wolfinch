#! /usr/bin/env python3
'''
# 
# Desc: Wolfinch notifier interface Implementation
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
from utils import getLogger
import time
import requests
import urllib

# mpl_logger.setLevel(logging.WARNING)
log = getLogger('Wolfinch')
log.setLevel(log.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)

Session = None
def post_url(url, data):
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
        log.info("initialized Wolfinch Session")
    log.info ("post url: %s"%(url))
    r = Session.post(url, data=data, timeout=15)
    if r.status_code == requests.codes.ok:
        return True
    else:
        log.error ("bad response code: %s resp: %s"%(str(r.status_code), r))
        return False

WOLFINCH_ADD_MARKET_API = "api/update_market"
class Notifier():
    def __init__(self, bot="", exchange="", token="", secret="", **kwarg):
        self.bot_url = bot
        self.exchange = exchange
        self.secret = secret
        self.token = token
        log.info("configured Wolfinch Notifier url: %s exchange %s token: %s secret: %s"%(bot, exchange, token, secret))
    def send_message (self, name, msg):
        log.debug ("msg: %s:%s"%(name, msg))
        if name == None or msg == None:
            return
        data = {
            "cmd" : "add",
            "req_code" : self.secret,
            "exch_name" : self.exchange,
            "product" : msg.get("symbol"),
        }
        URI = '%s/%s/%s' % (self.bot_url, self.token, WOLFINCH_ADD_MARKET_API)
        i = 0
        while i < 2:
            try:
                if True == post_url (URI, data):
                    log.debug("send msg success %s"%(data))
                    return True
                else:
                    log.error("failed ")
                    return False
            except requests.exceptions.ConnectionError as e:
                log.error("expection while Wolfinch send_msg.  retrying e: %s"%(e))
                time.sleep(2)
                i += 1

######### ******** MAIN ****** #########
if __name__ == '__main__':
    import traceback
    '''
    main entry point
    '''
    getcontext().prec = 8  # decimal precision
    print("Starting Wolfinch Client..")
    try:
        log.info("Starting Wolfinch")
        print("Starting Wolfinch")
        wfinch = Notifier(bot="http://localhost:8080", exchange="robinhood", token="2345", secret="1234")
        status = wfinch.send_message("wfinch", {"symbol":"NIO"})
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
    print("\n Wolfinch Client end")

# EOF
