# '''
#  Desc: Pivot points and support/resistance levels implementation
#
#  Copyright: (c) 2017-2023 Wolfinch Inc.
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

from datetime import datetime

# from decimal import Decimal
from .indicator import Indicator

class PIVOTPS (Indicator):
    '''
        Pivot points implementation
    '''
    period = 1
    def __init__(self, name, fibonaci=False):
        self.name = name
        self.fibonaci = fibonaci
        #states
        self.day_open = 0      
        self.day_high = 0      
        self.day_low = 0     
        self.day_close = 0
        self.day = 0
        self.pp = 0
        self.r1 = self.r2 = self.r3 = 0
        self.s1 = self.s2 = self.s3 = 0
        self.supstance = {}

    def calculate(self, candles):     
        cdl = candles[-1]['ohlc']
        dt = datetime.fromtimestamp(cdl.time)
        day = dt.date().day
        if  day != self.day:
            if self.day != 0:
                #skip the first day cdls, and setup support, resitstance levels.
                self.pp = (self.day_high + self.day_low + self.day_close)/3
                self.r1 = 2*self.pp - self.day_low
                self.r2 = self.pp + (self.day_high - self.day_low)
                self.r3 = self.day_high + 2*(self.pp - self.day_low)
                self.s1 = 2*self.pp - self.day_high
                self.s2 = self.pp - (self.day_high - self.day_low)
                self.s3 = self.day_low - 2*(self.day_high - self.pp)
                #cache PPs
                self.supstance = {"pp":self.pp,"r1": self.r1, "r2":self.r2, "r3":self.r3, "s1":self.s1, "s2":self.s2, "s3":self.s3}
            self.day = day
            self.open_time = cdl.time
            self.close_time = int(self.open_time + 6.5*3600) #market hrs are 6.5hrs
            self.day_open = cdl.open
            self.day_high = cdl.high
            self.day_low = cdl.low
            self.day_close = cdl.close        
        else:
            self.day_close = cdl.close 
            if self.day_high < cdl.high:
                self.day_high = cdl.high
            if self.day_low > cdl.low:
                self.day_low = cdl.low
        # now return 
        return self.supstance
        
