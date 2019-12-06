# '''
#  Desc: Average Directional Movement Index (Momentum Indicators) implementation using ta-lib
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
        
        close_array = np.array(map(lambda x: float(x['ohlc'].close), candles[-(self.period+20):]))
        high_array = np.array(map(lambda x: float(x['ohlc'].high), candles[-(self.period+20):]))
        low_array = np.array(map(lambda x: float(x['ohlc'].low), candles[-(self.period+20):]))
        
        #calculate 
        adx = talib.ADX (high_array, low_array, close_array, timeperiod=self.period)
        
        return adx[-1]
        
