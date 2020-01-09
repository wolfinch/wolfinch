# '''
#  Desc: Volume Oscilator (VOSC) implementation using tulip
#  https://tulipindicators.org/vosc
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

class VOSC (Indicator):
    '''  
    Desc: Volume Oscilator (VOSC) implementation using tulip market indicator implementation using TA library
    '''
    
    def __init__(self, name, short_period=14, long_period=21):
        self.name = name
        self.period = max(short_period, long_period)
        self.short_period = short_period
        self.long_period = long_period
                
    def calculate(self, candles):
        candles_len = len(candles)
        if candles_len < self.period+1:
            return float(0)
        
        val_array = np.array([float(x['ohlc'].volume) for x in candles[-(self.period+1):]])
        
        #calculate 
        vosc = ti.vosc (val_array, self.short_period, self.long_period)
#         print (vosc)
        return  float(vosc[-1])
                
