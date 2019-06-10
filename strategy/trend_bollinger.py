#
# OldMonk Auto trading Bot
# Desc:  trend_bollinger strategy
#
# Copyright 2018, OldMonk Bot. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from strategy import Strategy

class TREND_BOLLINGER(Strategy):
    def __init__ (self, name, upper_bound_pct=0, lower_bound_pct=0, period=50):     
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
        
        (upperBound, _, lowerBound) = self.get_indicator_current(candles, 'BBANDS')
        close = self.get_indicator_current(candles, 'close')

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