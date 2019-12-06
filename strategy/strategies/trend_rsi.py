#
# Wolfinch Auto trading Bot
# Desc:  Market Strategy Abstract Class Implementation
#
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

from strategy_base import Strategy
import numpy as np

class TREND_RSI(Strategy):
    config = {
        'period' : {'default': 20, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 2 }},
        'min_periods' : {'default': 52, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 2 }},
        'rsi_periods' : {'default': 14, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 2 }},    
        'oversold_rsi' : {'default': 30, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 2 }},
        'overbought_rsi' : {'default': 82, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 2 }},
        'rsi_recover' : {'default': 3, 'var': {'type': int, 'min': 1, 'max': 10, 'step': 1 }},
        'rsi_drop' : {'default': 0, 'var': {'type': int, 'min': 1, 'max': 10, 'step': 1 }},
        'rsi_divisor' : {'default': 2, 'var': {'type': int, 'min': 1, 'max': 10, 'step': 1 }},          
        }       
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
    
        #internal states
        self.trend = ''
        self.rsi_low = 0
        self.rsi_high = 0
        
        #CONFIGURE indicators
        self.set_indicator("RSI", {self.rsi_periods})
        self.set_indicator("close")
                
    def generate_signal (self, candles):
        '''
        Trade Signale in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        signal = 0
        len_candles = len (candles)

        if len_candles < self.period:
            return 0
        
#         rsi = np.array(map(lambda c: c['RSI14'], candles[:]))
#         cur_rsi = rsi[-1]
        
        cur_rsi = self.get_indicator_current(candles, 'RSI', self.rsi_periods)
        
        if cur_rsi == np.NaN:
            return 0
        if cur_rsi <= self.oversold_rsi:
            self.rsi_low = cur_rsi
            self.trend = 'oversold'
        if (self.trend == 'oversold') :
            self.rsi_low = min(self.rsi_low, cur_rsi)
            if (cur_rsi >= self.rsi_low + self.rsi_recover):
                self.rsi_high = cur_rsi                
                self.trend = 'long'
                signal = 3  #'strong buy'
        if (self.trend == 'long'):
            self.rsi_high = max (self.rsi_high, cur_rsi)
            if (cur_rsi <= self.rsi_high / self.rsi_divisor):
                self.trend = 'short'
                signal = -3 #sell
        if (self.trend == 'long' and cur_rsi >= self.overbought_rsi):
            self.rsi_high = cur_rsi
            self.trend = 'overbought'
        if (self.trend == 'overbought'):
            self.rsi_high = max(self.rsi_high, cur_rsi)
            if (cur_rsi <= self.rsi_high - self.rsi_drop):
                self.trend = 'short'
                signal = -3 #sell
        
        return signal
    
