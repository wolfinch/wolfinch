# '''
#  Desc: Money Flow Index (MFI) implementation using tulip
#  https://tulipindicators.org/mfi
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

class MFI (Indicator):
    '''
    Money Flow Index (MFI) market indicator implementation using TA library
    '''
    
    def __init__(self, name, period=14):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period+1:
            return float(0)
        
        high_a = np.array([float(x['ohlc'].high) for x in candles[-(self.period+1):]])
        low_a = np.array([float(x['ohlc'].low) for x in candles[-(self.period+1):]])
        close_a = np.array([float(x['ohlc'].close) for x in candles[-(self.period+1):]])        
        volume_a = np.array([float(x['ohlc'].volume) for x in candles[-(self.period+1):]])
        
        #calculate 
        cur_mfi = ti.mfi (high_a, low_a, close_a, volume_a, period=self.period)
        
        return float(cur_mfi[-1])
        
