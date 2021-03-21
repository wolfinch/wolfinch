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
from utils import getLogger
import yahoofin as yf
import time

log = getLogger('VOL_SPIKE')
log.setLevel(log.DEBUG)

class VOL_SPIKE(Screener):
    def __init__(self, name="VOL_SPIKE", ticker_kind="ALL", interval=300):
        log.info ("init: name: %s ticker_kind: %s interval: %d"%(name, ticker_kind, interval))
        super().__init__(name, ticker_kind, interval)
        self.YF = yf.Yahoofin ()
        li = [
         {"symbol": "aapl", "last_price": 10.2, "change": "10", "pct_change": "2"},
         {"symbol": "codx", "last_price": "13.2", "change": "20", "pct_change": "20"}            
             ]        
        self.filtered_list = li
    def update(self, sym_list, ticker_stats):
        get_all_tickers_info(self.YF, sym_list, ticker_stats)
        return True
    def screen(self, ticker_stats):
        pass
    def get_screened(self):
        self.filtered_list[0]["last_price"] += 1
        return self.filtered_list

def get_all_tickers_info(yf, sym_list, ticker_stats):
    BATCH_SIZE = 400
    log.debug("num tickers(%d)"%(len(sym_list)))
    i = 0
    while i < len(sym_list):
        ts, err =  yf.get_quotes(sym_list[i: i+BATCH_SIZE])
        if err == None:
            for ti in ts:
                s = ti.get("symbol")
                ss = ticker_stats.get(s)
                if ss == None:
                    ticker_stats[s] = {"info": ti, "time":[ti["regularMarketTime"]], "volume": [ti["regularMarketVolume"]], "price": [ti["regularMarketPrice"]]}
                else:
                    ss ["info"] = ti 
                    ss ["time"].append(ti["regularMarketTime"])
                    ss ["volume"].append(ti["regularMarketVolume"])
                    ss ["price"].append(ti["regularMarketPrice"])
            i += BATCH_SIZE
        else:
            time.sleep(2)
    log.debug("(%d)ticker stats retrieved"%( len(ticker_stats)))
    return ticker_stats
#EOF
