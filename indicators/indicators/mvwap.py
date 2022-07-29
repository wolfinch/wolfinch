# '''
#  Desc: Market Moving average Volume Weighted average price (MVWAP) implementation using tulip
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

# from decimal import Decimal
from .indicator import Indicator

class MVWAP (Indicator):
    '''
    Moving average Volume Weighted Average Price   (MVWAP) market indicator implementation
    '''
    
    def __init__(self, name, period=50, vwap_period=12):
        self.name = name
        self.period = period
        self.vwap_period = vwap_period
        
        #states
        self.cur_pv = 0
        self.cur_v = 0
        
        self.init = False
        self.old_vwap = 0
        self.vwap_list = []
        self.mvwap = 0
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return 0
        
        self.vwap_list.append(self._calculate_vwap(candles))
        self.mvwap += (self.vwap_list[-1])/self.period
        if len(self.vwap_list) > self.period:
            self.mvwap -= self.vwap_list[0]/self.period
            del(self.vwap_list[0])
        
        return self.mvwap
        
    def _calculate_vwap(self, candles):        
        if self.init == False:
            self.cur_pv = sum(map(lambda c: c['ohlc'].volume*((c['ohlc'].close + c['ohlc'].high + c['ohlc'].low)/3), candles[-self.vwap_period:-1]))
            self.cur_v = sum(map(lambda c: c['ohlc'].volume, candles[-self.vwap_period:-1]))
            old_pv = old_v = 0
            self.init = True
        else:
            ohlc = candles[-self.vwap_period]['ohlc']
            old_v = ohlc.volume                        
            old_pv = old_v*((ohlc.close + ohlc.high + ohlc.low)/3.0)
        
        ohlc = candles[-1]['ohlc']
        v = ohlc.volume
        pv = v * ((ohlc.close + ohlc.high + ohlc.low)/3.0)
        
        self.cur_pv = self.cur_pv - old_pv + pv
        self.cur_v = self.cur_v - old_v + v
        #calculate vwap
        
        return float(self.cur_pv / self.cur_v)
#EOF