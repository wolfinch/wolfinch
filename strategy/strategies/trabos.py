#
# Wolfinch Auto trading Bot
# Desc:  TRABOS (True Range Breakout) strategy
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

# Strategy (entry/exit):
# True range Breakeout
# Calculate the true range (daily high minus daily low).
# Buy signal is the closing price plus the true range.
# Sell signal is the closing price minus the true range.
# If long, the profit target is the daily high on the day of entry.
# If long, the protective stop is the low on the day of entry.
# If short, the profit target is the daily low on the day of entry.
# If short, the protective stop is the high on the day of entry.

#confirmation :
# 1. MFI - money flow index (MFI) should follow the market price. f.e. when asset making new high, MFI should make new high and vice versa
# 2. RSI - should follow market as above. (rule of thumb on RSI >70 overbought, <30, oversold)
# 3. Volume Oscilator (https://www.investopedia.com/articles/technical/02/082702.asp)
# def gen_sig():
    


# from decimal import Decimal
from .strategy import Strategy


class TRABOS(Strategy):
    # HoF :       #EMA_DEV{'strategy_cfg': {'ema_sell_s': 45, 'timeout_sell': 66, 'rsi': 34,
    # 'treshold_pct_buy_l': 1.71, 'ema_buy_s': 135, 'timeout_buy': 2, 'period': 110, 'treshold_pct_sell_s': 0.38,
    # 'ema_buy_l': 75, 'treshold_pct_sell_l': 0.49, 'treshold_pct_buy_s': 1.42, 'ema_sell_l': 95},
    # 'trading_cfg': {'take_profit_enabled': True, 'stop_loss_smart_rate': False, 'take_profit_rate': 20,
    # 'stop_loss_enabled': False, 'stop_loss_rate': 0}}
    config = {
        'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'atr' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},        
        'mfi' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'rsi' : {'default': 21, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'vosc_short' : {'default': 20, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'vosc_long' : {'default': 40, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},        
        'timeout_buy' : {'default': 50, 'var': {'type': int, 'min': 0, 'max': 100, 'step': 2 }},
        'timeout_sell' : {'default': 50, 'var': {'type': int, 'min': 0, 'max': 100, 'step': 2 }},
        }
    
    def __init__ (self, name, period=120, atr=60, mfi=50, sma=60, rsi=120, vosc_short=20, vosc_long=40,
                  timeout_buy=50, timeout_sell=50):     
        self.name = name
        self.period = period
    
        self.atr = atr
        self.sma = sma
        self.mfi = mfi
        self.rsi = rsi
        self.vosc_short = vosc_short
        self.vosc_long = vosc_long
        self.timeout_buy = timeout_buy
        self.timeout_sell = timeout_sell
        # internal states
        self.position = ''
        self.signal = 0
        self.cur_timeout_buy = timeout_buy
        self.cur_timeout_sell = timeout_sell    
        
        # configure required indicators
        self.set_indicator("ATR", {atr})        
        self.set_indicator("SMA", {sma})                
        self.set_indicator("MFI", {mfi})
        self.set_indicator("RSI", {rsi})
        self.set_indicator("VOSC", {(vosc_short, vosc_long)})        
        self.set_indicator("close")
        

    def generate_signal (self, candles):
#         '''
#         Trade Signal in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
#         '''
        len_candles = len (candles)

        signal = 0
        if len_candles < self.period:
            return 0
        
        
        rsi21 = self.indicator(candles, 'RSI', self.rsi)        
        mfi = self.indicator(candles, 'MFI', self.mfi)
        vosc = self.indicator(candles, 'VOSC', (self.vosc_short, self.vosc_long))
        cur_close = self.indicator(candles, 'close')
        
        atr = self.indicator(candles, 'ATR', self.atr)        
        sma = self.indicator(candles, 'SMA', self.sma)
        
        if cur_close > sma + atr:
#             print ("sma %f atr: %f close: %f"%(sma, atr, cur_close))
            return 1
        elif cur_close < sma + atr:
            return -1
#         print (rsi21, mfi, vosc)

        return signal
    
# EOF
