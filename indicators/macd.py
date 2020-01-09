# '''
#  Desc: Moving Average Convergence/Divergence (Momentum Indicators) implementation using tulip
#  https://tulipindicators.org/macd
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

class MACD (Indicator):
    '''
    Moving Average Convergence/Divergence (Momentum Indicators) implementation using TA library
    default:         fastperiod: 12
        slowperiod: 26
        signalperiod: 9
        period = slowperiod + signal - 1
    '''
    
    def __init__(self, name, short_period=34, long_period=34, signal_period=34):
        self.name = name
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.long_period:
            return (0, 0, 0)
        
        close_array = np.array([float(x['ohlc'].close) for x in candles[-self.period:]])
        
        #calculate 
        (macd, macdsignal, macdhist) = ti.macd (close_array, short_period=self.short_period,
                                                long_period=self.long_period,
                                                signal_period=self.signal_period)
        
        return (macd[-1], macdsignal[-1], macdhist[-1])
        
