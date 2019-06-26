#
# OldMonk Auto trading Bot
# Desc:  EMA_DEV strategy
# strategy based on - https://github.com/R4nd0/ema_dev/blob/master/strategy.js
#
# Copyright 2019, OldMonk Bot. All Rights Reserved.
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
from strategy_base import Strategy

class EMA_DEV(Strategy):
    config = {
        'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema_buy_s' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema_buy_l' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema_sell_s' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema_sell_l' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'treshold_pct_buy_s' : {'default': 1, 'var': {'type': float, 'min': 0, 'max': 2, 'step': 0.2 }},
        'treshold_pct_buy_l' : {'default': 1.5, 'var': {'type': float, 'min': 0, 'max': 2, 'step': 0.2 }},
        'treshold_pct_sell_s' : {'default': 0.8, 'var': {'type': float, 'min': 0, 'max': 2, 'step': 0.2 }},
        'treshold_pct_sell_l' : {'default': 1, 'var': {'type': float, 'min': 0, 'max': 2, 'step': 0.2 }},        
        }
    
    def __init__ (self, name, period=120, ema_buy_s=50, ema_buy_l=120, ema_sell_s=50, ema_sell_l=120,
                  treshold_pct_buy_s=1, treshold_pct_buy_l=1.5, treshold_pct_sell_s=0.8, treshold_pct_sell_l=1,
                  timeout_buy = 50, timeout_sell = 50):     
        self.name = name
        self.period = period
    
        self.ema_buy_s = ema_buy_s
        self.ema_buy_l = ema_buy_l
        self.ema_sell_s = ema_sell_s
        self.ema_sell_l = ema_sell_l
        self.treshold_pct_buy_s = Decimal(treshold_pct_buy_s)
        self.treshold_pct_buy_l = Decimal(treshold_pct_buy_l)
        self.treshold_pct_sell_s = Decimal(treshold_pct_sell_s)
        self.treshold_pct_sell_l = Decimal(treshold_pct_sell_l)
        self.timeout_buy = timeout_buy
        self.timeout_sell = timeout_sell
        #internal states
        self.position = ''
        self.signal = 0
        self.cur_timeout_buy = timeout_buy
        self.cur_timeout_sell = timeout_sell    
        
        #configure required indicators
        self.set_indicator("EMA", {ema_buy_s, ema_buy_l, ema_sell_s, ema_sell_l})
        self.set_indicator("RSI", {21})
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
        rsi21 = self.get_indicator_current(candles, 'RSI', 21)        
        ema_buy_s = self.get_indicator_current(candles, 'EMA', self.ema_buy_s)
        ema_buy_l = self.get_indicator_current(candles, 'EMA', self.ema_buy_l)
        ema_sell_s = self.get_indicator_current(candles, 'EMA', self.ema_sell_s)
        ema_sell_l = self.get_indicator_current(candles, 'EMA', self.ema_sell_l)
        
        cur_close = self.get_indicator_current(candles, 'close')

#         if ema13 > ema21:
#             self.trend = 'bullish'
#         else:
#             self.trend = 'bearish'
#         
        if ((cur_close >= ema_sell_s *(1 + (1 * self.treshold_pct_sell_s/100))) and 
            (cur_close >= ema_sell_l * (1 + (1 * self.treshold_pct_sell_l/100))) and 
            (self.cur_timeout_sell < 0 )):
            
            signal = -3 # sell
            self.cur_timeout_sell = self.timeout_sell
        elif ((cur_close <= ema_buy_s *(1 + (1 * self.treshold_pct_buy_s/100))) and 
            (cur_close <= ema_buy_l  * (1 + (1 * self.treshold_pct_buy_l/100))) and 
            (self.cur_timeout_sell < 0 )):
            
            signal = 3 # buy
            self.cur_timeout_buy = self.timeout_buy
        else:
            self.cur_timeout_buy -= 1
            self.cur_timeout_sell -= 1
        
        return signal
    
#EOF