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

from sqlalchemy import true
from utils import getLogger
import tweepy 

# mpl_logger.setLevel(logging.WARNING)
log = getLogger('Twitter')
log.setLevel(log.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)

class Notifier():
    def __init__(self, api_key="", api_key_secret="", access_token="", access_token_secret="", **kwarg):
        self.api_key =api_key 
        self.api_key_secret = api_key_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.client = tweepy.Client(consumer_key=api_key, consumer_secret=api_key_secret,
            access_token=access_token, access_token_secret=access_token_secret)
        log.info("configured twitter Notifier consumer_key: %s, consumer_secret: %s, access_token: %s, access_token_secret: %s, **kwarg: %s"%( 
        api_key, api_key_secret, access_token, access_token_secret, kwarg))
    def send_message (self, name, pos):
        log.info ("msg: %s - %s "%(name, pos))
        if name == None or pos == None:
            log.error ("invalid msg")
            return
        response = self.client.create_tweet(text=self._pos_to_msg(name, pos), user_auth=True)
        log.debug ("resp %s", response)
    def _pos_to_msg(self, name, pos_str):
        return "%s: %s"%(name, pos_str)[:140]
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
        ApiKey = ""
        ApiKeySecret = ""
        AccessToken = ""
        AccessTokenSecret = ""
        
        twit = Notifier(ApiKey, ApiKeySecret, AccessToken, AccessTokenSecret)
        status = twit.send_message("oh hi lol! :-p")
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
