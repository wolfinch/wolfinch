# '''
#  Desc: On Balance Volume (OBV) implementation 
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

# from decimal import Decimal
from .indicator import Indicator

class OBV (Indicator):
    '''
        On Balance Volume (OBV) implementation
        1. If today's closing price is higher than yesterday's closing price, then: Current OBV = Previous OBV + today's volume
        
        2. If today's closing price is lower than yesterday's closing price, then: Current OBV = Previous OBV - today's volume
        
        3. If today's closing price equals yesterday's closing price, then: Current OBV = Previous OBV        
    '''
    period = 1    
    def __init__(self, name):
        self.name = name
        
        #internal states
        self.obv_prev = 0
        self.close_prev = 0
                
    def calculate(self, candles):        
        if not len(candles) :
            return float(0)
        
        cdl_cur = candles[-1]['ohlc']
        if cdl_cur.close > self.close_prev:
            obv = self.obv_prev + cdl_cur.volume
        elif cdl_cur.close < self.close_prev:
            obv = self.obv_prev - cdl_cur.volume
        else:
            # c = c_prev
            obv = self.obv_prev

        self.obv_prev = obv
        self.close_prev = cdl_cur.close
        return float(obv)
        
