# '''
#  Desc: Market Volume Exponential Moving Average Oscilator (VEMAOSC) implementation 
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

from .indicator import Indicator

class VEMAOSC (Indicator):
    '''
    Volume Exponential Moving Average Oscilator (VEMAOSC) implementation 
    '''
    
    def __init__(self, name, short_period=14, long_period=21):
        self.name = name
        self.period = max(short_period, long_period)
        self.short_period = short_period
        self.long_period = long_period
        
        self._short_multiplier = float(2.0)/ (short_period +1)
        self._long_multiplier = float(2.0)/ (long_period +1)
        
        #internal states
        self.prev_vema_short = 0        
        self.prev_vema_long = 0
                
    def calculate(self, candles):
        # The formula below is for a 10-day EMA:
        # 
        # SMA: 10 period sum / 10 
        # Multiplier: (2 / (Time periods + 1) ) = (2 / (10 + 1) ) = 0.1818 (18.18%)
        # EMA: {Close - EMA(previous day)} x multiplier + EMA(previous day). 
        
        candles_len = len(candles)
        if candles_len < self.period:
            return float(0)
        
        if self.prev_vema_short == 0:
            #SMA 
            self.prev_vema_short =  float(sum( map (lambda x: x['ohlc'].volume, candles[-self.short_period:])))/self.short_period
        if self.prev_vema_long == 0:
            #SMA 
            self.prev_vema_long =  float(sum( map (lambda x: x['ohlc'].volume, candles[-self.long_period:])))/self.long_period
                
        
        #calculate ema
        self.prev_vema_short = float(((candles[candles_len - 1]['ohlc'].volume - self.prev_vema_short )*self._short_multiplier + self.prev_vema_short))
        self.prev_vema_long = float(((candles[candles_len - 1]['ohlc'].volume - self.prev_vema_long )*self._long_multiplier + self.prev_vema_long))
        
        
        return 100*(self.prev_vema_short - self.prev_vema_long)/self.prev_vema_long
        
