# '''
#  Desc: Market Simple Moving Average (SMA) implementation 
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

class SMA (Indicator):
    '''
    Simple moving Average (SMA) market indicator implementation
    '''
    
    def __init__(self, name, period=15):
        self.name = name
        self.period = period
                
    def calculate(self, candles):
        if len(candles) < self.period:
            return 0
        #(time, o, h,l,c, vol)
        return  float(sum( [x['ohlc'].close for x in candles[-self.period:]]))/self.period
        
