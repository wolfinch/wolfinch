#
# OldMonk Auto trading Bot
# Desc:  TRIX_RSI strategy
# strategy based on - https://www.investopedia.com/articles/technical/02/092402.asp
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


# from decimal import Decimal
from strategy_base import Strategy

# from utils import getLogger
# 
# log = getLogger ('decision_simple')
# log.setLevel(log.CRITICAL)

class TRIX_RSI(Strategy):
    config = {
        'period' : {'default': 80, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'rsi' : {'default': 21, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 2 }},
        'trix' : {'default': 30, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 2 }},        
        'rsi_overbought_level' : {'default': 70, 'var': {'type': int, 'min': 50, 'max': 100, 'step': 2 }},
        'rsi_oversold_level' : {'default': 30, 'var': {'type': int, 'min': 20, 'max': 70, 'step': 2 }},      
        }       
    def __init__ (self, name, period=80, rsi=21, trix=30, rsi_overbought_level=70, rsi_oversold_level=30):     
        self.name = name
        self.period = period
        self.rsi = rsi
        self.trix = trix        
        self.rsi_overbought = rsi_overbought_level
        self.rsi_oversold = rsi_oversold_level
    
        #internal states
        self.trend = ''
        self.signal = 0
        self.acted_on_trend = False
        
        #Configure indicators
        self.set_indicator("RSI", {self.rsi})
        self.set_indicator("TRIX", {self.trix})
                
    def generate_signal (self, candles):
        '''
        Trade Signale in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        signal = 0
        len_candles = len (candles)

        if len_candles < self.period:
            return 0
        
        rsi21 = self.get_indicator_current(candles, 'RSI', self.rsi)
        trix30 = round(self.get_indicator_current(candles, 'TRIX', self.trix), 2)

        if trix30 > 0:
            #'up' trend
#             log.critical("TRIX(%f) UP RSI(%f) close(%f)"%(trix30, rsi21, candles[-1]['ohlc'].close))    
            if self.trend != 'up' or self.acted_on_trend:
                if self.trend != 'up':
                    #trend reversal                    
#                     log.critical("REVERSAL >>> TRIX(%f) UP"%(trix30))
                    self.acted_on_trend = False
                    self.trend = 'up'                                    
                if not self.acted_on_trend:
#                     log.critical("ACT ON TREND TRIX(%f) UP"%(trix30))
                    self.acted_on_trend = True
                    signal = 1
                if rsi21 <= self.rsi_oversold:
#                     log.critical("RSI(%f) OVERSOLD TRIX(%f) UP"%(rsi21, trix30))
                    self.acted_on_trend = False
                    signal = 3
        elif trix30 < 0 :
            #'down' trend
#             log.critical("TRIX(%f) DOWN RSI(%f) close(%f)"%(trix30, rsi21, candles[-1]['ohlc'].close))
            if self.trend != 'down' or self.acted_on_trend:
                if self.trend != 'down':
#                     log.critical("REVERSAL >>> TRIX(%f) DOWN"%(trix30))                
                    #trend reversal
                    self.trend = 'down'
                    self.acted_on_trend = False
                if not self.acted_on_trend:
#                     log.critical("ACT ON TREND TRIX(%f) DOWN"%(trix30))                    
                    self.acted_on_trend = True
                    signal = -1
                if rsi21 >= self.rsi_overbought:
#                     log.critical("RSI(%f) OVERBOUGHT TRIX(%f) DOWN"%(rsi21, trix30))                    
                    self.acted_on_trend = False       
                    signal = -3  
        else:
#             self.trend = ''
            pass
        
        return signal        
#EOF
    