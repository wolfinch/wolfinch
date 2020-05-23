# '''
#  Desc: Average Directional Movement Index (Momentum Indicators) implementation using tulip
#  https://tulipindicators.org/adx
#
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

class ADX (Indicator):
    '''
    Average Directional Movement Index (Momentum Indicators) implementation using TA library
    '''
    
    def __init__(self, name, period=14):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period+20: #make sure 20 more candles are available to work with
            return 0
        
        close_array = np.array([float(x['ohlc'].close) for x in candles[-(self.period+20):]])
        high_array = np.array([float(x['ohlc'].high) for x in candles[-(self.period+20):]])
        low_array = np.array([float(x['ohlc'].low) for x in candles[-(self.period+20):]])
        
        #calculate 
        adx = ti.adx (high_array, low_array, close_array, self.period)
        
        return adx[-1]
        
