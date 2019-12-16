#
# Wolfinch Auto trading Bot
# Desc:  RSI_MACD_TREND strategy
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
from .strategy import Strategy


class RSI_MACD_TREND(Strategy):
    # HoF :       #EMA_DEV{'strategy_cfg': {'ema_sell_s': 45, 'timeout_sell': 66, 'rsi': 34,
    # 'treshold_pct_buy_l': 1.71, 'ema_buy_s': 135, 'timeout_buy': 2, 'period': 110, 'treshold_pct_sell_s': 0.38,
    # 'ema_buy_l': 75, 'treshold_pct_sell_l': 0.49, 'treshold_pct_buy_s': 1.42, 'ema_sell_l': 95},
    # 'trading_cfg': {'take_profit_enabled': True, 'stop_loss_smart_rate': False, 'take_profit_rate': 20,
    # 'stop_loss_enabled': False, 'stop_loss_rate': 0}}
    config = {
        'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema_buy_s' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema_buy_l' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema_sell_s' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema_sell_l' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'rsi' : {'default': 21, 'var': {'type': int, 'min': 10, 'max': 100, 'step': 1 }},
        'treshold_pct_buy_s' : {'default': 1, 'var': {'type': float, 'min': 0, 'max': 2, 'step': 0.2 }},
        'treshold_pct_buy_l' : {'default': 1.5, 'var': {'type': float, 'min': 0, 'max': 2, 'step': 0.2 }},
        'treshold_pct_sell_s' : {'default': 0.8, 'var': {'type': float, 'min': 0, 'max': 2, 'step': 0.2 }},
        'treshold_pct_sell_l' : {'default': 1, 'var': {'type': float, 'min': 0, 'max': 2, 'step': 0.2 }},
        'timeout_buy' : {'default': 50, 'var': {'type': int, 'min': 0, 'max': 100, 'step': 2 }},
        'timeout_sell' : {'default': 50, 'var': {'type': int, 'min': 0, 'max': 100, 'step': 2 }},
        }
    
    def __init__ (self, name, period=120, ema_buy_s=50, ema_buy_l=120, ema_sell_s=50, ema_sell_l=120,
                  treshold_pct_buy_s=1, rsi=21, treshold_pct_buy_l=1.5, treshold_pct_sell_s=0.8, treshold_pct_sell_l=1,
                  timeout_buy=50, timeout_sell=50):     
        self.name = name
        self.period = period
    
        self.ema_buy_s = ema_buy_s
        self.ema_buy_l = ema_buy_l
        self.ema_sell_s = ema_sell_s
        self.ema_sell_l = ema_sell_l
        self.treshold_pct_buy_s = float(treshold_pct_buy_s)
        self.treshold_pct_buy_l = float(treshold_pct_buy_l)
        self.treshold_pct_sell_s = float(treshold_pct_sell_s)
        self.treshold_pct_sell_l = float(treshold_pct_sell_l)
        self.timeout_buy = timeout_buy
        self.timeout_sell = timeout_sell
        self.rsi = rsi
        # internal states
        self.position = ''
        self.signal = 0
        self.cur_timeout_buy = timeout_buy
        self.cur_timeout_sell = timeout_sell    
        
        # configure required indicators
        self.set_indicator("EMA", {ema_buy_s, ema_buy_l, ema_sell_s, ema_sell_l})
        self.set_indicator("RSI", {rsi})
        self.set_indicator("close")
        

    def generate_signal (self, candles):
#         '''
#         Trade Signal in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
#         '''
        len_candles = len (candles)

        signal = 0
        if len_candles < self.period:
            return 0
        
#         cur_rsi = rsi[-1]
        rsi21 = self.indicator(candles, 'RSI', self.rsi)        
        ema_buy_s = self.indicator(candles, 'EMA', self.ema_buy_s)
        ema_buy_l = self.indicator(candles, 'EMA', self.ema_buy_l)
        ema_sell_s = self.indicator(candles, 'EMA', self.ema_sell_s)
        ema_sell_l = self.indicator(candles, 'EMA', self.ema_sell_l)
        
        cur_close = self.indicator(candles, 'close')


        return signal
    
# EOF
