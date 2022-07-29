#! /usr/bin/env python3
# '''
#  Wolfinch Auto trading Bot
#  Desc: Yahoofin exchange interactions for Wolfinch
#
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
# '''

import json
import base64
import hmac
import hashlib
import time
from threading import Thread
import threading
from websocket import create_connection, WebSocketConnectionClosedException
from utils import getLogger
from .yahoofin_pricingdata_pb2 import PricingData

parser = args = None
log = getLogger ('YahoofinWS')
log.setLevel(log.DEBUG)

WS_BASE = "wss://streamer.finance.yahoo.com/"
class WebsocketClient(object):
    def __init__(self, url=WS_BASE, products=None, feed_recv_hook=None):
        self.url = url
        if products:
            self.products = products
#         self.channels = channels
#         self.type = message_type
        self.stop = True
        self.error = None
        self.ws = None
        self.thread = None
        if feed_recv_hook :
            self.feed_recv_hook = feed_recv_hook
        else:
            self.feed_recv_hook = self.dummy_on_recv
#         self.auth = auth
#         self.api_key = api_key
#         self.api_secret = api_secret
#         self.api_passphrase = api_passphrase
#         self.should_print = should_print
#         self.mongo_collection = mongo_collection

    def dummy_on_recv(self, msg):
        log.info ("msg_recv: %s"%(msg))

    def subscribe(self, feed_list=None):
        if feed_list:
            if not isinstance(feed_list, list):
                feed_list = [feed_list]
            if not self.products:
                self.products = feed_list
            else:
                self.products+= feed_list
        if self.ws and self.products:
            cmd = {"subscribe": self.products}
            log.info ("subscribe feed_list: %s"%(json.dumps(cmd)))
            self.ws.send(json.dumps(cmd))
        
    def start(self):
        log.info ("starting WebsocketClient")
        
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.ws_error = False            
        self.on_open()
        self.thread = Thread(target=_go)
        self.thread.start()        
        
        self.hearbeat_time = time.time()
        self.keepalive_thread = Thread(target=self._keepalive)
        self.keepalive_thread.start()
    
    def restart (self):
        self.thread.join()
        log.info ("restarting cbproWebsocketClient")
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False          
        self.ws_error = False            
        self.on_open()
        self.thread = Thread(target=_go)
        self.thread.start()
    def close(self):
        log.info ("closing ws and keep alive threads")
        self.stop = True
        self._disconnect()
        self.thread.join()
        log.debug ("waiting to close alive threads")            
        self.keepalive_thread.join()
        log.debug ("closed ws and keep alive threads")     
                
    def _keepalive(self, interval=3):
        while not self.stop :
            #TODO: FIXME: potential race
            if self.hearbeat_time + 600 < (time.time()):
                #heartbeat failed
                log.error ("Heartbeat failed!! last_hb_time: %d cur_time: %d \
                potential websocket death, restarting"%(self.hearbeat_time, time.time()))
                if (self.stop):
                    log.info ("websocket attempt close intentionally")
                    break
                log.debug ("before ws restart. active thread count: %d"% threading.active_count())                     
                self.restart()
                log.debug ("after ws restart. active thread count: %d"% threading.active_count())
            time.sleep(interval)
        
    def on_open(self):
        self.message_count = 0
        log.info("Let's count the messages!")

    def on_message(self, msg):
        pd = PricingData()
        pd.ParseFromString(base64.b64decode(msg))        
        self.feed_recv_hook(pd)
        #print(json.dumps(msg, indent=4, sort_keys=True))
        self.message_count += 1

    def on_close(self):
        print("\n-- Goodbye! --")
        
    def on_error(self, e, data=None):
        self.error = e
        self.ws_error = True
        log.critical('error: %s - data: %s'%(e, data))
           
    #to fix the connection drop bug
    def _listen(self):
        self.time = time.time()
        while not self.stop and not self.ws_error:
            try:
                start_t = 0
                if time.time() - start_t >= 30:
                    # Set a 30 second ping to keep connection alive
                    self.ws.ping("keepalive")
                    start_t = time.time()
                msg = self.ws.recv()
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                self.hearbeat_time = time.time()
                self.on_message(msg)
#             if (self.stop): 
#                 log.info ("ws listen finished. waiting to finish keepalive thread")
#                 self.keepalive_thread.join()

    def _connect(self):
        if self.url[-1] == "/":
            self.url = self.url[:-1]

#         if self.auth:
#             timestamp = str(time.time())
#             message = timestamp + 'GET' + '/users/self/verify'
#             auth_headers = get_auth_headers(timestamp, message, self.api_key, self.api_secret, self.api_passphrase)
#             sub_params['signature'] = auth_headers['CB-ACCESS-SIGN']
#             sub_params['key'] = auth_headers['CB-ACCESS-KEY']
#             sub_params['passphrase'] = auth_headers['CB-ACCESS-PASSPHRASE']
#             sub_params['timestamp'] = auth_headers['CB-ACCESS-TIMESTAMP']

        self.ws = create_connection(self.url)
        self.subscribe()

    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            log.error("exception while websocket close e: %s"%(e))
            pass
        self.on_close()

if __name__ == "__main__":
    import sys

    class MyWebsocketClient(WebsocketClient):
        def on_open(self):
            self.products = ["LYFT"] #, "ES=F", "YM=F", "NQ=F", "RTY=F", "CL=F", "GC=F", "SI=F", "EURUSD=X", "^TNX", "^VIX"]
            self.message_count = 0
            print("Let's count the messages!")
        def on_message(self, msg):
            pd = PricingData()
            pd.ParseFromString(base64.b64decode(msg))
#             print(json.dumps(msg, indent=4, sort_keys=True))
            print (" type:%s \n msg: %s time: %d"%(type(pd), pd, pd.time))
            self.message_count += 1
            
    wsClient = MyWebsocketClient()
    wsClient.start()
    print(wsClient.url, wsClient.products)
    try:
        while True:
            print("\nMessageCount =", "%i \n" % wsClient.message_count)
            time.sleep(1)
    except KeyboardInterrupt:
        wsClient.close()

    if wsClient.error:
        sys.exit(1)
    else:
        sys.exit(0)

# EOF