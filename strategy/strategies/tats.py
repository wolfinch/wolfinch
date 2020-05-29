#
# Wolfinch Auto trading Bot
# Desc:  TATS (Truly Amazing Trading Strategy)
#
#  Copyright: (c) 2017-2020 Joshith Rayaroth Koderi
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

from datetime import datetime
from .strategy import Strategy


class TATS(Strategy):
    config = {
        'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema' : {'default': 5, 'var': {'type': int, 'min': 2, 'max': 30, 'step': 1 }},                
        'atr' : {'default': 50, 'var': {'type': int, 'min': 10, 'max': 200, 'step': 5 }},        
        'mfi' : {'default': 50, 'var': {'type': int, 'min': 10, 'max': 200, 'step': 5 }},
        'mfi_dir_len' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 10, 'step': 1 }},  
        'obv_dir_len' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 10, 'step': 1 }},          
        'stop_x' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 10, 'step': 1 }},        
        'profit_x' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 10, 'step': 1 }},                      
        'vosc_short' : {'default': 20, 'var': {'type': int, 'min': 10, 'max': 80, 'step': 5 }},
        'vosc_long' : {'default': 40, 'var': {'type': int, 'min': 40, 'max': 200, 'step': 5 }},    
        'timeout_buy' : {'default': 5, 'var': {'type': int, 'min': 0, 'max': 50, 'step': 2 }},
        'timeout_sell' : {'default': 5, 'var': {'type': int, 'min': 0, 'max': 50, 'step': 2 }},            
        }
    
    def __init__ (self, name, period=480, ema=6, atr=60, mfi=50, mfi_dir_len=20, obv_dir_len=20,
                  vosc_short=20, vosc_long=40, stop_x=2, profit_x=2,
                  timeout_buy=5, timeout_sell=5
                 ):
        self.name = name
        self.period = period
    
        self.atr = atr
        self.ema = ema
        self.mfi = mfi
        self.mfi_dir_len = 2 #mfi_dir_len
        self.rsi_dir_len = 2
        self.obv_dir_len = obv_dir_len
        self.stop_x = stop_x
        self.profit_x = profit_x
        self.vosc_short = 10 #vosc_short
        self.vosc_long = 100 #vosc_long
        self.timeout_buy = timeout_buy
        self.timeout_sell = timeout_sell
        self.rsi = 10
        self.atr_mx = 2
        
        # internal states
        self.signal = 0
        self.cur_timeout_buy = timeout_buy
        self.cur_timeout_sell = timeout_sell    
        
        # configure required indicators
        self.set_indicator("ATR", atr)
        self.set_indicator("EMA", ema)                
        self.set_indicator("MFI", mfi)
        #self.set_indicator("VOSC", {(vosc_short, vosc_long)}) 
#         self.set_indicator("OBV")
        self.set_indicator("RSI", self.rsi)
        self.set_indicator("VEMAOSC", (self.vosc_short, self.vosc_long))
        self.set_indicator("close")
        self.set_indicator("VWAP")
#         self.set_indicator("MVWAP", (250, vwap))
        
        # states
        self.day_open = 0      
        self.day_high = 0      
        self.day_low = 0     
        self.day_close = 0
        self.day = 0
        self.pp = 0
        self.r1 = self.r2 = self.r3 = 0
        self.s1 = self.s2 = self.s3 = 0
        self.r_l = {}
        self.s_l = {}
        self.rsi_trend = ""
        self.res_try_break = False
        self.open_time = 0
        self.close_time = 0
    def generate_signal (self, candles):
#         '''
#         Trade Signal in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
#         '''
        #   rsi oversold/bought
        # mfi and rsi are in same direction
        # relate with support/resistance on movement
        # trend reversal (signal)
        len_candles = len (candles)
        signal = 0
        if len_candles < self.period:
            return 0
        cdl = candles[-1]['ohlc']
        dt = datetime.fromtimestamp(cdl.time)
        day = dt.date().day
        if  day != self.day:
            if self.day != 0:
                #skip the first day cdls, and setup support, resitstance levels.
                self.pp = (self.day_high + self.day_low + self.day_close)/3
                self.r1 = 2*self.pp - self.day_low
                self.s1 = 2*self.pp - self.day_high
                self.r2 = self.pp + (self.day_high - self.day_low)
                self.s2 = self.pp - (self.day_high - self.day_low)
                self.r3 = self.day_high + 2*(self.pp - self.day_low)
                self.s3 = self.day_low - 2*(self.day_high - self.pp)
                self.s_l = {self.s1:0, self.s2:0, self.s3:0}
                self.r_l = {self.r1:0, self.r2:0, self.r3:0}
                print ("setting up levels for day: %d s1: %f r1: %f s2: %f r2: %f s3: %f r3: %f"%(day, self.s1, self.r1, self.s2, self.r2, self.s3, self.r3))                
            self.day = day
            self.open_time = cdl.time
            self.close_time = int(self.open_time + 6.5*3600)
            self.day_open = cdl.open
            self.day_high = cdl.high
            self.day_low = cdl.low
            self.day_close = cdl.close 
        else:
            self.day_close = cdl.close 
            if self.day_high < cdl.high:
                self.day_high = cdl.high
            if self.day_low > cdl.low:
                self.day_low = cdl.low
        mfi_l = self.indicator(candles, 'MFI', self.mfi, history=self.mfi_dir_len)
        rsi_l = self.indicator(candles, 'RSI', self.rsi, history=self.rsi_dir_len)
        
        vosc = self.indicator(candles, 'VEMAOSC', (self.vosc_short, self.vosc_long))
        cur_close = self.indicator(candles, 'close')
        
#         obv_l = self.indicator(candles, 'OBV', history=self.obv_dir_len)
        
        atr = self.indicator(candles, 'ATR', self.atr)
        ema_l = self.indicator(candles, 'EMA', self.ema, history=2)
        vwap = self.indicator(candles, 'VWAP')
        rsi = rsi_l[-1]
        
        #short trend, simple direction
        if ema_l[0] > ema_l[-1]:
            trend = "down"
        else:
            trend = "up"
        signal = 0
        #support/resistance zone handling
        if trend == "up":
            #see if we are near any resistance zones or crossed
            for r in list(self.r_l.keys()):
                #czse 1. moving up from resistance
                if cur_close >= r + self.atr_mx*atr:
                    #resistance crossed, flip roles - resistance becomes support now
                    self.s_l[r] = self.r_l[r]+1
                    del(self.r_l[r])
#                     break #could we break multiple resistance in one candle? yes!
                elif cur_close >= r - self.atr_mx*atr:
                    #case 2: trying to break resistance. within the reange now.
                    self.res_try_break = True
            #case 2. moving up from support, nothing to do.(should we buy from here??)
        elif trend == "down":
            #see if we are near any support zones or crossed
            for s in list(self.s_l.keys()):
                #case 1: support broke. we might go down further. sell. 
                if cur_close <= s - self.atr_mx*atr:
                    #support broke, flip roles
                    self.r_l[s] = self.s_l[s]+1
                    del(self.s_l[s])
                    signal -= 1
            #case 2: tried break resistance and failed. we could go further down. sell
            if self.res_try_break:
                signal -= 1
                self.res_try_break = False
        if rsi > 60:
            self.rsi_trend = "OB"
        elif rsi <25:
            self.rsi_trend = "OS"
        elif rsi >= 30 and rsi <= 60:
            self.rsi_trend = ""
        
        if (self.rsi_trend == "OS" and 
            all(mfi_l[i] <= mfi_l[i+1] for i in range(len(mfi_l)-1)) and 
            all(rsi_l[i] <= rsi_l[i+1] for i in range(len(rsi_l)-1))):
            #recovering
            signal += 1
        elif (self.rsi_trend == "OB" and 
              all(mfi_l[i] >= mfi_l[i+1] for i in range(len(mfi_l)-1)) and 
              all(rsi_l[i] >= rsi_l[i+1] for i in range(len(rsi_l)-1))):
            signal -= 1
# #             and all( obv_l[i] <= obv_l[i+1] for i in range(len(obv_l)-1))
# #             and all( obv_l[i] <= obv_l[i+1] for i in range(len(obv_l)-1))
#         if ((cur_close > ema + atr) and (vosc > 0) and (vwap > ema)
#             and all( mfi_l[i] <= mfi_l[i+1] for i in range(len(mfi_l)-1)) 
# #             and all( obv_l[i] <= obv_l[i+1] for i in range(len(obv_l)-1))
#             and (self.cur_timeout_buy <= 0)):      
#             self.cur_timeout_buy = self.timeout_buy           
#             return 1, cur_close-self.stop_x*atr, cur_close+self.profit_x*atr
#         elif ((cur_close < ema - atr and vosc > 0) and (vwap < ema)
#               and (self.cur_timeout_sell <= 0)):
# #             if (all( mfi_l[i] >= mfi_l[i+1] for i in range(len(mfi_l)-1))):    
#             self.cur_timeout_sell = self.timeout_sell        
#             return -1
#         else:
#             self.cur_timeout_buy -= 1
#             self.cur_timeout_sell -= 1            
#             return signal
#         print ("cdl time; %d opentime: %d %d "%(cdl.time , self.open_time + 30*60, self.close_time))
        if cdl.time < self.open_time + 15*60:
            # we are a day trading strategy and let's not carry over to next day
            #let's not buy anything within half n hr of market open and sell everything 15min in to market close            
            signal = 0
        elif cdl.time > self.close_time - 15*60:
            signal = -1  
        return signal
    
# EOF
