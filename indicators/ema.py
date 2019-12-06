# '''
#  Desc: Market Exponential Moving Average (EMA) implementation 
#  Copyright: (c) 2017-2019 Joshith Rayaroth Koderi
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

from indicator import Indicator

class DEFUNCT_EMA (Indicator):
    '''
    Exponential moving Average (EMA) market indicator implementation
    '''
    
    def __init__(self, name, period=12):
        self.name = name
        self.period = period
        self._multiplier = float(2)/ (period +1)
                
    def calculate(self, candles):
        # The formula below is for a 10-day EMA:
        # 
        # SMA: 10 period sum / 10 
        # Multiplier: (2 / (Time periods + 1) ) = (2 / (10 + 1) ) = 0.1818 (18.18%)
        # EMA: {Close - EMA(previous day)} x multiplier + EMA(previous day). 
        
        candles_len = len(candles)
        if candles_len < self.period:
            return float(0)
        
        prev_ema = candles[candles_len - 2][self.name]
        if prev_ema == 0:
            #SMA 
            prev_ema =  float(sum( map (lambda x: x['ohlc'].close, candles)))/self.period
        
        #calculate ema
        return float(((candles[candles_len - 1]['ohlc'].close - prev_ema )*self._multiplier + prev_ema))
        
