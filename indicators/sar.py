# '''
#  Desc: Parabolic SAR (Overlap Studies) implementation using ta-lib
#  (c) https://mrjbq7.github.io/ta-lib/
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
import numpy as np
import talib

class SAR (Indicator):
    '''
    Parabolic SAR (Overlap Studies) implementation using TA library
    '''
    
    def __init__(self, name, period=20):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return 0
        
        high_array = np.array(map(lambda x: float(x['ohlc'].high), candles[-self.period:]))
        low_array = np.array(map(lambda x: float(x['ohlc'].low), candles[-self.period:]))
        
        #calculate 
        sar = talib.SAR (high_array, low_array)
        
        return sar[-1]
        
