#
# Wolfinch Auto trading Bot
# Desc:  EMA_RSI strategy
# strategy based on - https://www.mql5.com/en/forum/197614
#
# Copyright 2018, Wolfinch Bot. All Rights Reserved.
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

# from decimal import Decimal
from strategy_base import Strategy
import numpy as np

class EMA_RSI_SLOW(Strategy):
    #HoF -       #EMA_RSI: {'rsi': 64, 'ema_s': 44, 'period': 38, 'ema_m': 184, 'ema_l': 156, 'ema_ll': 64}
    config = {
        'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'ema_s' : {'default': 5, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'ema_m' : {'default': 13, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'ema_l' : {'default': 21, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'ema_ll' : {'default': 80, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'rsi' : {'default': 21, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 1 }},   
        'rsi_bullish_mark' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 100, 'step': 2 }},   
        'buy_pause_time' : {'default': 50, 'var': {'type': int, 'min': 2, 'max': 60, 'step': 2 }},                     
        'sell_pause_time' : {'default': 50, 'var': {'type': int, 'min': 2, 'max': 60, 'step': 2 }},                                               
        }
    # best: {'rsi': 64, 'ema_s': 30, 'period': 38, 'ema_m': 200, 'ema_l': 120, 'ema_ll': 60}
    def __init__ (self, name, period=80, ema_s=5, ema_m=13, ema_l=21, ema_ll=80, rsi=21, rsi_bullish_mark=50,
                  buy_pause_time=0, sell_pause_time=0):     
        self.name = name
        self.period = period
        self.ema_s = ema_s
        self.ema_m = ema_m
        self.ema_l = ema_l
        self.ema_ll = ema_ll
        self.rsi = rsi
        self.rsi_bullish_mark = rsi_bullish_mark
        self.buy_pause_time = buy_pause_time
        self.sell_pause_time = sell_pause_time

        
        #internal states
        self.position = ''
        self.signal = 0
        self.cur_buy_pause_time = 0
        self.cur_sell_pause_time = 0
        
        #configure required indicators
        self.set_indicator("EMA", {self.ema_s, self.ema_m, self.ema_l, self.ema_ll})
        self.set_indicator("RSI", {self.rsi})
        #self.set_indicator("close")
                
    def generate_signal (self, candles):
        '''
        Trade Signale in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        signal = 0
        len_candles = len (candles)

        if len_candles < self.period:
            return 0
        
#         rsi = np.array(map(lambda c: c['RSI21'], candles[:]))
#         cur_rsi = rsi[-1]
        rsi21 = self.get_indicator_current(candles, 'RSI', self.rsi)        
        ema5 = self.get_indicator_current(candles, 'EMA', self.ema_s)
        ema13 = self.get_indicator_current(candles, 'EMA', self.ema_m)
        ema21 = self.get_indicator_current(candles, 'EMA', self.ema_l)
        ema80 = self.get_indicator_current(candles, 'EMA', self.ema_ll)
        
        if ema13 > ema21:
            self.trend = 'bullish'
        else:
            self.trend = 'bearish'
            
        # clear signal
        self.signal  = 0
        if rsi21 > self.rsi_bullish_mark: #bullish market
            if self.position == 'sell': #trend reversal, cancel position #TODO: FIXME: implement closing position
                self.position = '' 
                self.signal = 1
#                 return self.signal
            if self.position == 'buy' and ema5 < ema13 and ema5 < ema21: #close buy position
                self.position = '' 
                self.signal = -1
#                 return self.signal
            if self.trend == 'bullish' and ema5 > ema13 and ema5 > ema21 and ema21 > ema80 and ema13 > ema80:
#                 if self.position == 'buy': #if trend continues, increase signal strength
#                     self.signal += 1
#                     if self.signal >= 3:
#                         self.signal = 3
#                         self.cur_buy_pause_time = self.buy_pause_time
                if self.cur_buy_pause_time < 0:
                    self.position = 'buy'
                    self.signal = 3  # buy
                    self.cur_buy_pause_time = self.buy_pause_time
        else: # bearish market
            if self.position == 'buy': #trend reversal, cancel position #TODO: FIXME: implement closing position
                self.position = '' 
                self.signal = -1
                #return self.signal                
            if self.position == 'sell' and ema5 > ema13 and ema5 > ema21: #close sell position (short)
                self.position = '' 
                self.signal = 1
                #return self.signal
            if self.trend == 'bearish' and ema5 < ema13 and ema5 < ema21 and ema21 < ema80 and ema13 < ema80:
#                 if self.position == 'sell': #if trend continues, increase signal strength
#                     self.signal -= 1
#                     if self.signal < -3:
#                         self.signal = -3
#                         self.cur_sell_pause_time = self.sell_pause_time                        
#                 else:            
                if self.cur_sell_pause_time < 0:    
                    self.position = 'sell'
                    self.signal = -3 # sell
                    self.cur_sell_pause_time = self.sell_pause_time 
                    
        self.cur_buy_pause_time -= 1
        self.cur_sell_pause_time -= 1          
        
        return self.signal 
    
