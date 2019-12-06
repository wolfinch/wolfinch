#
# Wolfinch Auto trading Bot
# Desc:  MINMAX strategy (Trade if candle close is min or max of history periods.)
# strategy based on - https://www.reddit.com/r/zenbot/comments/b92mis/minmax_strategy/
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

from decimal import Decimal
from strategy_base import Strategy

class MINMAX(Strategy):
    #{'strategy_cfg': {'timeout_sell': 56, 'period': 32, 'timeout_buy': 36}, 'trading_cfg': {'take_profit_rate': 0, 'stop_loss_smart_rate': True, 'take_profit_enabled': False, 'stop_loss_enabled': True, 'stop_loss_rate': 8}}
    config = {
        'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'timeout_buy' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},
        'timeout_sell' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 2 }},      
        }    
    
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
