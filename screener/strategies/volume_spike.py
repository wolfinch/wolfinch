#
# Wolfinch Auto trading Bot screener
#
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

# from decimal import Decimal
from .screener_base import Screener
import yahoofin as yf
import time
from datetime import datetime
import notifiers

from utils import getLogger

log = getLogger("VOL_SPIKE")
log.setLevel(log.DEBUG)

class VOL_SPIKE(Screener):
    def __init__(self, name="VOL_SPIKE", ticker_kind="ALL", interval=300, vol_multiplier=2):
        log.info ("init: name: %s ticker_kind: %s interval: %d"%(name, ticker_kind, interval))
        super().__init__(name, ticker_kind, interval)
        self.YF = yf.Yahoofin ()
        self.vol_multiplier = vol_multiplier
        self.filtered_list = {} #li
    def update(self, sym_list, ticker_stats):
        #update stats only during ~12hrs, to cover pre,open,ah (5AM-5PM PST, 12-00UTC)
        if datetime.utcfromtimestamp(int(time.time())).hour <= 12 :
            log.debug("market closed")
            return False
        try:
            get_all_tickers_info(self.YF, sym_list, ticker_stats)
            return True
        except Exception as e:
            log.critical("exception while get data e: %s"%(e))
            return False
    def screen(self, sym_list, ticker_stats):
        #1. if cur vol >= 2x10davg vol
        #2. renew once a day 
        now = int(time.time())
        if len(self.filtered_list):
            #prune filtered list
            s_l = []
            for sym, info in self.filtered_list.items() :
                if info["time"] + 4*24*60*60 < now :
                    s_l.append(sym)
            for s_e in s_l:
                log.info ("del "+s_e)
                del self.filtered_list[s_e]
        for sym in sym_list:
#             log.debug("sym info: %s"%(info))
            info = ticker_stats.get(sym)
            if info == None:
                continue
            rmv = info["info"].get("regularMarketVolume", -1)
            adv10 = info["info"].get("averageDailyVolume10Day", -1)
            rmp = info["info"].get("regularMarketPrice", -1)
            rmcp = info["info"].get("regularMarketChangePercent", -1)
            if (rmv != -1 and adv10 != -1 and rmv != 0 and adv10 != 0) and (
                rmv > self.vol_multiplier*adv10):
                fs = self.filtered_list.get(sym)
                if (fs == None or (fs["time"] + 12*60*60 < now)):
                    fs  = {"symbol": sym, "time": now,
                           "last_price": round(rmp, 2),
                           "price_change": round(rmcp, 2),
                           "cur_price_change": round(rmcp, 2),                           
                           "vol_change": round(100*(rmv - adv10)/adv10, 1),
                           "cur_vol_change": round(100*(rmv - adv10)/adv10, 1)                           
                           }
                    log.info ('new sym found by screener: %s info:  %s'%(sym, fs))
                    
                    self.filtered_list [sym] = fs
                    notify_msg = "%s price %s(%s%%) vol %s%%"%(fs["symbol"], fs["last_price"], fs["price_change"],
                                                                       fs["vol_change"])
                    notifiers.notify(self.name, notify_msg)
                else:
                    fs["cur_price_change"] = round(rmcp, 2)
                    fs["cur_vol_change"] = round(100*(rmv - adv10)/adv10, 1)
                    
    def get_screened(self):
#         ft = [
#          {"symbol": "aapl", "time": 1616585400, "last_price": 10.2, "price_change": "10", "vol_change": "2", "cur_price_change": "20", "cur_vol_change": "4"},
#          {"symbol": "codx", "time": 1616595400, "last_price": "13.2", "price_change": "20", "vol_change": "20", "cur_price_change": "30", "cur_vol_change": "30"}            
#              ]
        fmt = {"symbol": "symbol", "time": "time", "last_price": "last price", 
               "price_change": "% price", "cur_price_change": "% cur price", "vol_change": "% vol", "cur_vol_change": "% cur vol"}
        return [fmt]+list(self.filtered_list.values())
#         return [fmt]+ft

def get_all_tickers_info(yf, sym_list, ticker_stats):
    BATCH_SIZE = 400
#     log.debug("num tickers(%d)"%(len(sym_list)))
    s = None
    ss = None
    i = 0
    try:
        while i < len(sym_list):
            ts, err =  yf.get_quotes(sym_list[i: i+BATCH_SIZE])
            if err == None:
                for ti in ts:
                    s = ti.get("symbol")
                    ss = ticker_stats.get(s)
                    if ss == None:
                        ticker_stats[s] = {"info": ti, "time":[ti.get("regularMarketTime", 0)],
                                            "volume": [ti.get("regularMarketVolume", -1)], "price": [ti.get("regularMarketPrice", -1)]
                                            }
                    else:
                        ss ["info"] = ti                      
                        ss ["time"].append(ti.get("regularMarketTime", 0))
                        ss ["volume"].append(ti.get("regularMarketVolume", -1))
                        ss ["price"].append(ti.get("regularMarketPrice", -1))
                        #limit history
                        if len(ss["time"]) > 1024:
                            del(ss["time"][0])
                            del(ss["volume"][0])
                            del(ss["price"][0])                       
                i += BATCH_SIZE
            else:
                log.critical ("yf api failed err: %s i: %d num: %d"%(err, i, len(sym_list)))
                time.sleep(2)
    except Exception as e:
        log.critical (" Exception e: %s \n s: %s ss: %s i: %d len: %d"%(e, s, ss, i, len(sym_list)))
        raise e
    log.debug("(%d)ticker stats retrieved"%( len(ticker_stats)))
    return ticker_stats
#EOF
