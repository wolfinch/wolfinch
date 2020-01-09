# '''
#  Desc: Relative Strength Index (Momentum Indicators) implementation using tulip
#  https://tulipindicators.org/rsi
#  Copyright: (c) 2017-2020 Joshith Rayaroth Koderi
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
import numpy as np
import tulipy as ti

class RSI (Indicator):
    '''
    Relative Strength Index (Momentum Indicators) market indicator implementation using TA library
    '''
    
    def __init__(self, name, period=14):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period+1:
            return float(0)
        
        val_array = np.array([float(x['ohlc'].close) for x in candles[-(self.period+1):]])
        
        #calculate 
        cur_rsi = ti.rsi (val_array, period=self.period)
        
        return float(cur_rsi[-1])
        
