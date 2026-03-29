#
# Wolfinch Auto trading Bot
# Desc:  NOOBS_DT (noobs day trading strategy)
#
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

#confirmation :
# buy in the morning 30min after market open
# sell in the evening 30 mins before market close

from datetime import datetime
from .strategy import Strategy

class NOOBS_DT(Strategy):
    config = {
#         'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
         'open_delay' : {'default': 30, 'var': {'type': int, 'min': 1, 'max': 200, 'step': 1 }},
         'close_delay' : {'default': 30, 'var': {'type': int, 'min': 1, 'max': 200, 'step': 1 }},
        }
    
    def __init__ (self, name, period=30, open_delay=30, close_delay=30):
        self.name = name
        self.period = period
        self.open_delay = open_delay
        self.close_delay = close_delay
        self.bought = False
        self.day = 0
        self.set_indicator("close")

    def generate_signal (self, candles):
#         '''
#         Trade Signal in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
#         '''
        len_candles = len (candles)
        if len_candles < self.period:
            return 0        
        signal = 0
        cdl = candles[-1]['ohlc']
        dt = datetime.fromtimestamp(cdl.time)
        day = dt.date().day
        if  day != self.day:
            self.day = day
            self.open_time = cdl.time
            self.close_time = int(self.open_time + 6.5*3600) #market hrs are 6.5hrs
            self.day_open = cdl.open
            self.day_high = cdl.high
            self.day_low = cdl.low
            self.day_close = cdl.close
            print("******###########################\n\n new day(%d) \n################################*******"%(day))            

        if (self.bought == False and (cdl.time >= self.open_time + self.open_delay*60) and 
                 (cdl.time < self.close_time - self.close_delay*60)) :
            #buy after open delay and before close delay
            signal = 1
            self.bought = True
            print ("TATS - buy signal: %d"%(signal))            
        elif self.bought == True and cdl.time >= self.close_time - self.close_delay*60:
            # we are a day trading strategy and let's not carry over to next day            
            signal = -1
            self.bought = False
            print ("TATS - closing day window. SELL everything signal: %d"%(signal))            
        return signal
    
# EOF
