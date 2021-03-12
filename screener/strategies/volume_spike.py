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

class VOL_SPIKE(Screener):
    def __init__(self, interval=300):
        super().__init__("VOL_SPIKE", interval)
#         self.name = "VOL_SPIKE"
#         self.interval = interval
    def update(self):
        pass
    def screen(self):
        pass
    def get_screened(self):
        pass

def get_all_tickers_info(ticker_stats):
    BATCH_SIZE = 400
    sym_list = get_all_tickers()
    log.debug("num tickers(%d)"%(len(sym_list)))
#     ticker_stats = []
    i = 0
#     t = int(time.time())
    while i < len(sym_list):
        ts, err =  YF.get_quotes(sym_list[i: i+BATCH_SIZE])
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
