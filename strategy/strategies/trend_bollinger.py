#
# Wolfinch Auto trading Bot
# Desc:  trend_bollinger strategy
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

from .strategy import Strategy

class TREND_BOLLINGER(Strategy):
    config = {
        'period' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'upper_bound_pct' : {'default': 0, 'var': {'type': int, 'min': 0, 'max': 100, 'step': 2 }},
        'lower_bound_pct' : {'default': 0, 'var': {'type': int, 'min': 0, 'max': 100, 'step': 2 }},      
        }       
    def __init__ (self, name, period=50, upper_bound_pct=0, lower_bound_pct=0):     
        self.name = name
        self.period = period
        self.bollinger_upper_bound_pct = upper_bound_pct
        self.bollinger_lower_bound_pct = lower_bound_pct
    
        #internal states
        self.position = ''
        self.signal = 0
        self.trend = ''
        self.last_hit_bollinger = ''
        self.last_hit_close = 0
        
        #configure required indicators
        self.set_indicator("BBANDS")
        self.set_indicator("close")
                
    def generate_signal (self, candles):
        '''
        Trade Signal in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        len_candles = len (candles)

        if len_candles < self.period:
            return 0
        
        (upperBound, _, lowerBound) = self.indicator(candles, 'BBANDS')
        close = self.indicator(candles, 'close')

        self.signal = 0 # hold        
        if (upperBound and lowerBound):
            if (close > (upperBound / 100) * (100 - self.bollinger_upper_bound_pct)):
                self.last_hit_bollinger = 'upper'
            elif (close < (lowerBound / 100) * (100 + self.bollinger_lower_bound_pct)):
                self.last_hit_bollinger = 'lower'
            else:
                if (self.last_hit_bollinger == 'upper' and close < self.last_hit_close):
                    self.trend = 'down'
                elif (self.last_hit_bollinger == 'lower' and close > self.last_hit_close):
                    self.trend = 'up'
                self.last_hit_bollinger = 'middle'
            self.last_hit_close = close
    
            if (self.trend == 'down'):
                #sell
                self.signal = -3
                self.trend = None
            elif (self.trend == 'up'):
                #buy
                self.signal = 3
                self.trend = None
        
        return self.signal
    
#EOF
