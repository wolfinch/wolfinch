#
# OldMonk Auto trading Bot
# Desc:  EMA_RSI strategy
# strategy based on - https://www.mql5.com/en/forum/197614
#
# Copyright 2018, Joshith Rayaroth Koderi. All Rights Reserved.
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
import numpy as np

class EMA_RSI(Strategy):
    def __init__ (self, name, period=80):     
        self.name = name
        self.period = period
    
        #internal states
        self.position = ''
        self.signal = 0
    def generate_signal (self, candles):
        '''
        Trade Signale in range(-5..0..5), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        signal = 0
        len_candles = len (candles)

        if len_candles < self.period:
            return 0
        
#         rsi = np.array(map(lambda c: c['RSI21'], candles[:]))
#         cur_rsi = rsi[-1]
        rsi21 = candles[-1]['RSI21']
        
        ema5 = candles[-1]['EMA5']
        ema13 = candles[-1]['EMA13']
        ema21 = candles[-1]['EMA21']
        ema80 = candles[-1]['EMA80']
        
        if rsi21 > 50: #bullish market
            if self.position == 'sell': #trend reversal, cancel position #TODO: FIXME: implement closing position
                self.position = '' 
                self.signal = 0
            if ema5 > ema13 and ema5 > ema21 and ema21 > ema80 and ema13 > ema80:
                if self.position == 'buy': #if trend continues, increase signal strength
                    self.signal += 1
                    if self.signal > 5:
                        self.signal = 5
                else:
                    self.position = 'buy'
                    self.signal = 3  # buy
        else: # bearish market
            if self.position == 'buy': #trend reversal, cancel position #TODO: FIXME: implement closing position
                self.position = '' 
                self.signal = 0            
            if ema5 < ema13 and ema5 < ema21 and ema21 < ema80 and ema13 < ema80:
                if self.position == 'sell': #if trend continues, increase signal strength
                    self.signal -= 1
                    if self.signal < -5:
                        self.signal = -5
                else:                
                    self.position = 'sell'
                    self.signal = -3 # sell
        
        return signal
    