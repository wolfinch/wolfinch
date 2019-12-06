# '''
#  Desc: Moving Average Convergence/Divergence (Momentum Indicators) implementation using ta-lib
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

class MACD (Indicator):
    '''
    Moving Average Convergence/Divergence (Momentum Indicators) implementation using TA library
    default:         fastperiod: 12
        slowperiod: 26
        signalperiod: 9
        period = slowperiod + signal - 1
    '''
    
    def __init__(self, name, period=34):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return (0, 0, 0)
        
        close_array = np.array(map(lambda x: float(x['ohlc'].close), candles[-self.period:]))
        
        #calculate 
        (macd, macdsignal, macdhist) = talib.MACD (close_array)
        
        return (macd[-1], macdsignal[-1], macdhist[-1])
        
