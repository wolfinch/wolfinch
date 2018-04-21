#
# OldMonk Auto trading Bot
# Desc:  Market Strategy Abstract Class Implementation
# Copyright 2018, Joshith Rayaroth Koderi. All Rights Reserved.
#
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

class TREND_RSI(Strategy):
    def __init__ (self, name, period=20,
                  min_periods=52, rsi_periods=14, oversold_rsi=30, overbought_rsi=82,
                  rsi_recover=3, rsi_drop=0, rsi_divisor=2):
        ''' 
        Init for the strategy
      this.option('period_length', 'period length, same as --period', String, '2m')
      this.option('min_periods', 'min. number of history periods', Number, 52)
      this.option('rsi_periods', 'number of RSI periods', 14)
      this.option('oversold_rsi', 'buy when RSI reaches or drops below this value', Number, 30)
      this.option('overbought_rsi', 'sell when RSI reaches or goes above this value', Number, 82)
      this.option('rsi_recover', 'allow RSI to recover this many points before buying', Number, 3)
      this.option('rsi_drop', 'allow RSI to fall this many points before selling', Number, 0)
      this.option('rsi_divisor', 'sell when RSI reaches high-water reading divided by this value', Number, 2)        
        '''       
        self.name = name
        self.period = period
        self.min_periods = min_periods
        self.rsi_periods = rsi_periods
        self.oversold_rsi = oversold_rsi
        self.overbought_rsi = overbought_rsi
        self.rsi_recover = rsi_recover
        self.rsi_drop = rsi_drop
        self.rsi_divisor = rsi_divisor
    
    def generate_signal (self, candles):
        '''
        Trade Signale in range(-5..0..5), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        rsi_high = rsi_low = signal = 0
        trend = ''
        len_candles = len (candles)

        if len_candles < self.period:
            return 0
        
        rsi = np.array(map(lambda c: c['rsi'], candles[:]))
        cur_rsi = rsi[-1]
        
        if cur_rsi == np.NaN:
            return 0
        if cur_rsi <= self.oversold_rsi:
            rsi_low = cur_rsi
            trend = 'oversold'
        if (trend == 'oversold') :
            rsi_low = min(rsi_low, cur_rsi)
            if (cur_rsi >= rsi_low + self.rsi_recover):
                rsi_high = cur_rsi                
                trend = 'long'
                signal = 5  #'strong buy'
        if (trend == 'long'):
            rsi_high = max (rsi_high, cur_rsi)
            if (cur_rsi <= rsi_high / self.rsi_divisor):
                trend = 'short'
                signal = -5 #sell
        if (trend == 'long' and cur_rsi >= self.overbought_rsi):
            rsi_high = cur_rsi
            trend = 'overbought'
        if (trend == 'overbought'):
            rsi_high = max(rsi_high, cur_rsi)
            if (cur_rsi <= rsi_high - self.rsi_drop):
                trend = 'short'
                signal = -5 #sell
        
        return signal
    