#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: Main File implements Bot
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

from .indicator import Indicator

# import numpy as np
# import talib

class NOOP (Indicator):
    '''
     No-Op indicator 
    '''
    def __init__(self, name):
        self.name = name
        self.period = 1
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len == 0:
            return 0
        return float(candles[-1]['ohlc'].close)
        
