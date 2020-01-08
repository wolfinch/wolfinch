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
    

from .strategy import Strategy


class TRABOS(Strategy):
    config = {
        'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'sma' : {'default': 5, 'var': {'type': int, 'min': 2, 'max': 30, 'step': 1 }},                
        'atr' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},        
        'mfi' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'mfi_dir_len' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 10, 'step': 1 }},  
        'stop_x' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 10, 'step': 1 }},        
        'profit_x' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 10, 'step': 1 }},                      
        'vosc_short' : {'default': 20, 'var': {'type': int, 'min': 10, 'max': 80, 'step': 5 }},
        'vosc_long' : {'default': 40, 'var': {'type': int, 'min': 40, 'max': 200, 'step': 5 }},    
        'timeout_buy' : {'default': 5, 'var': {'type': int, 'min': 0, 'max': 50, 'step': 2 }},
        'timeout_sell' : {'default': 5, 'var': {'type': int, 'min': 0, 'max': 50, 'step': 2 }},            
        }
    
    def __init__ (self, name, period=120, sma=6, atr=60, mfi=50, mfi_dir_len=20,
                  vosc_short=20, vosc_long=40, stop_x=2, profit_x=2,
                  timeout_buy=5, timeout_sell=5
                 ):
        self.name = name
        self.period = period
    
        self.atr = atr
        self.sma = sma
        self.mfi = mfi
        self.mfi_dir_len = mfi_dir_len
        self.stop_x = stop_x
        self.profit_x = profit_x
        self.vosc_short = vosc_short
        self.vosc_long = vosc_long
        self.timeout_buy = timeout_buy
        self.timeout_sell = timeout_sell
        
        # internal states
        self.signal = 0
        self.cur_timeout_buy = timeout_buy
        self.cur_timeout_sell = timeout_sell    
        
        # configure required indicators
        self.set_indicator("ATR", {atr})        
        self.set_indicator("SMA", {sma})                
        self.set_indicator("MFI", {mfi})
        self.set_indicator("VOSC", {(vosc_short, vosc_long)}) 
        self.set_indicator("OBV")
        self.set_indicator("close")
        

    def generate_signal (self, candles):
#         '''
#         Trade Signal in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
#         '''
        len_candles = len (candles)

        signal = 0
        if len_candles < self.period:
            return 0
                
        mfi_l = self.indicator(candles, 'MFI', self.mfi, history=self.mfi_dir_len)
        vosc = self.indicator(candles, 'VOSC', (self.vosc_short, self.vosc_long))
        cur_close = self.indicator(candles, 'close')
        obv_l = self.indicator(candles, 'OBV', history=4)
        
        atr = self.indicator(candles, 'ATR', self.atr)        
        sma = self.indicator(candles, 'SMA', self.sma)
        
        if ((cur_close > sma + atr and vosc > 0) 
            and all( mfi_l[i] <= mfi_l[i+1] for i in range(len(mfi_l)-1)) 
            and all( obv_l[i] <= obv_l[i+1] for i in range(len(obv_l)-1))
            and (self.cur_timeout_buy < 0)):      
            self.cur_timeout_buy = self.timeout_buy           
            return 1, cur_close-self.stop_x*atr, cur_close+self.profit_x*atr
        elif ((cur_close < sma - atr and vosc > 0)
              and (self.cur_timeout_sell < 0)):
#             if (all( mfi_l[i] >= mfi_l[i+1] for i in range(len(mfi_l)-1))):    
            self.cur_timeout_sell = self.timeout_sell        
            return -1
        else:
            self.cur_timeout_buy -= 1
            self.cur_timeout_sell -= 1            
            return signal
    
# EOF
