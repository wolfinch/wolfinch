#
# OldMonk Auto trading Bot
# Desc:  MINMAX strategy (Trade if candle close is min or max of history periods.)
# strategy based on - https://www.reddit.com/r/zenbot/comments/b92mis/minmax_strategy/
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

from decimal import Decimal
from strategy import Strategy

class MINMAX(Strategy):
    def __init__ (self, name, period=120,
                  timeout_buy = 50, timeout_sell = 50):     
        self.name = name
        self.period = period
    
        self.timeout_buy = timeout_buy
        self.timeout_sell = timeout_sell
        #internal states
        self.position = ''
        self.signal = 0
        self.cur_timeout_buy = timeout_buy
        self.cur_timeout_sell = timeout_sell
        
        #configure required indicators
        self.set_indicator("close")   
             
    def generate_signal (self, candles):
        '''
        Trade Signale in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        len_candles = len (candles)

        signal = 0
        if len_candles < self.period:
            return 0
        
#         cur_rsi = rsi[-1]
#         rsi21 = candles[-1]['RSI21']

        close_l = [a['close'] for a in candles[-self.period:]]

        cur_min = min(close_l)
        cur_max = max(close_l)
        cur_close = close_l[-1]
        
        if ((cur_close >= cur_max) and 
            (self.cur_timeout_sell < 0 )):
            
            signal = -3 # sell
            self.cur_timeout_sell = self.timeout_sell
        elif ((cur_close <= cur_min) and 
            (self.cur_timeout_sell < 0 )):
            
            signal = 3 # buy
            self.cur_timeout_buy = self.timeout_buy
        else:
            self.cur_timeout_buy -= 1
            self.cur_timeout_sell -= 1
        
        return signal
    
#EOF