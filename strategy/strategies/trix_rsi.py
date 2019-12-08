#
# Wolfinch Auto trading Bot
# Desc:  TRIX_RSI strategy
# strategy based on - https://www.investopedia.com/articles/technical/02/092402.asp
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


# from decimal import Decimal
from .strategy_base import Strategy

# from utils import getLogger
# 
# log = getLogger ('decision_simple')
# log.setLevel(log.CRITICAL)

# Hof 
# {'strategy_cfg': {'rsi_oversold_level': 66, 'period': 76, 'trix': 10, 'rsi': 24, 'rsi_overbought_level': 78}, 'trading_cfg': {'take_profit_rate': 0, 'stop_loss_smart_rate': False, 'take_profit_enabled': False, 'stop_loss_enabled': False, 'stop_loss_rate': 0}}
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
    
