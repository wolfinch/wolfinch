#
# Wolfinch Auto trading Bot
# Desc:  TATS (Truly Amazing Trading Strategy)
#
#  Copyright: (c) 2017-2022 Wolfinch Inc.
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

#confirmation :
# 1. MFI - money flow index (MFI) should follow the market price. f.e. when asset making new high, MFI should make new high and vice versa
# 2. RSI - should follow market as above. (rule of thumb on RSI >70 overbought, <30, oversold)
# 3. Volume Oscilator (https://www.investopedia.com/articles/technical/02/082702.asp)
# def gen_sig():

from sortedcontainers import sorteddict
from datetime import datetime
from .strategy import Strategy
from utils import getLogger

log = getLogger ('TATS')
log.setLevel(log.DEBUG)

class TATS(Strategy):
    config = {
#         'period' : {'default': 120, 'var': {'type': int, 'min': 20, 'max': 200, 'step': 5 }},
        'ema' : {'default': 5, 'var': {'type': int, 'min': 2, 'max': 30, 'step': 1 }},
        'atr' : {'default': 50, 'var': {'type': int, 'min': 10, 'max': 80, 'step': 5 }}, 
        'rsi' : {'default': 14, 'var': {'type': int, 'min': 10, 'max': 90, 'step': 2 }},
        'mfi' : {'default': 50, 'var': {'type': int, 'min': 10, 'max': 90, 'step': 2 }},
        'mfi_dir_len' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 5, 'step': 1 }},  
        'rsi_dir_len' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 5, 'step': 1 }},          
        'rsi_overbought' : {'default': 70, 'var': {'type': int, 'min': 50, 'max': 90, 'step': 2 }},
        'rsi_oversold' : {'default': 20, 'var': {'type': int, 'min': 15, 'max': 40, 'step': 2 }},
#         'obv_dir_len' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 10, 'step': 1 }},
        'open_delay' : {'default': 2, 'var': {'type': int, 'min': 2, 'max': 30, 'step': 2 }},
        'close_delay' : {'default': 2, 'var': {'type': int, 'min': 10, 'max': 30, 'step': 2 }},
        'atr_mx' : {'default': 2, 'var': {'type': int, 'min': 1, 'max': 5, 'step': 1 }},
#         'vosc_short' : {'default': 20, 'var': {'type': int, 'min': 10, 'max': 80, 'step': 5 }},
#         'vosc_long' : {'default': 40, 'var': {'type': int, 'min': 40, 'max': 200, 'step': 5 }},    
#         'timeout_buy' : {'default': 5, 'var': {'type': int, 'min': 0, 'max': 50, 'step': 2 }},
#         'timeout_sell' : {'default': 5, 'var': {'type': int, 'min': 0, 'max': 50, 'step': 2 }},
        }
    
    def __init__ (self, name, period=30, ema=6, ema_l=24, atr=50, mfi=50, rsi=14, rsi_overbought=70, rsi_oversold=20,
                  open_delay=20, close_delay=15, atr_mx=2, mfi_dir_len=2, rsi_dir_len=2
                 ):
        self.name = name
        self.period = period
    
        self.atr = atr
        self.ema = ema
        self.ema_l = ema_l
        self.mfi = mfi
        self.mfi_dir_len = mfi_dir_len #mfi_dir_len
        self.rsi_dir_len = rsi_dir_len
#         self.obv_dir_len = obv_dir_len
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
#         self.vosc_short = 10 #vosc_short
#         self.vosc_long = 100 #vosc_long
        self.open_delay = open_delay
        self.close_delay = close_delay
        self.rsi = rsi
        self.atr_mx = atr_mx
        
        # internal states
        self.signal = 0
#         self.cur_timeout_buy = timeout_buy
#         self.cur_timeout_sell = timeout_sell
        
        # configure required indicators
        self.set_indicator("ATR", atr)
        self.set_indicator("EMA", ema)
        self.set_indicator("EMA", ema_l)        
        self.set_indicator("MFI", mfi)
        #self.set_indicator("VOSC", {(vosc_short, vosc_long)}) 
#         self.set_indicator("OBV")
        self.set_indicator("RSI", self.rsi)
#         self.set_indicator("VEMAOSC", (self.vosc_short, self.vosc_long))
        self.set_indicator("close")
        self.set_indicator("VWAP")
#         self.set_indicator("MVWAP", (250, vwap))
#         self.set_indicator("MACD", (24, 52, 9))

        # states
        self.day_open = 0      
        self.day_high = 0      
        self.day_low = 0     
        self.day_close = 0
        self.day = 0
        self.pp = 0
        self.r1 = self.r2 = self.r3 = 0
        self.s1 = self.s2 = self.s3 = 0
        self.r_l = sorteddict.SortedDict()
        self.s_l = sorteddict.SortedDict()
        self.zone_action = ""
        self.rsi_action = ""        
        self.rsi_trend = ""
        self.res_try_break = False
        self.sup_try_break = False
        self.vwap_try_break = False
        self.open_time = 0
        self.close_time = 0
        self.bought = True
        self.trend = ""

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
                self.s_l = sorteddict.SortedDict({self.s1:0, self.s2:0, self.s3:0, self.pp:0})
                self.r_l = sorteddict.SortedDict({self.r1:0, self.r2:0, self.r3:0})
                log.debug ("setting up levels for day: %d high: %f low: %f close: %f open: %f"%(day, self.day_high, self.day_low, self.day_close, self.day_open))                
            self.day = day
            self.open_time = cdl.time
            self.close_time = int(self.open_time + 6.5*3600) #market hrs are 6.5hrs
            self.day_open = cdl.open
            self.day_high = cdl.high
            self.day_low = cdl.low
            self.day_close = cdl.close
            log.debug("******###########################\n\n new day(%d) \n################################*******"%(day))            
        else:
            self.day_close = cdl.close 
            if self.day_high < cdl.high:
                self.day_high = cdl.high
            if self.day_low > cdl.low:
                self.day_low = cdl.low
        if len_candles < self.period:
            return 0
        mfi_l = self.indicator(candles, 'MFI', self.mfi, history=self.mfi_dir_len)
        rsi_l = self.indicator(candles, 'RSI', self.rsi, history=self.rsi_dir_len)
        
#         vosc = self.indicator(candles, 'VEMAOSC', (self.vosc_short, self.vosc_long))
        cur_close = self.indicator(candles, 'close')
        
#         obv_l = self.indicator(candles, 'OBV', history=self.obv_dir_len)
        
        atr = self.indicator(candles, 'ATR', self.atr)
        ema_sh = self.indicator(candles, 'EMA', self.ema, history=2)
        ema_s = ema_sh[-1]
        ema_l = self.indicator(candles, 'EMA', self.ema_l)        
        vwap = self.indicator(candles, 'VWAP')
        rsi = rsi_l[-1]
        
        #simple direction
        if ema_sh[0] > ema_sh[-1]:
            dir = "down"
        elif ema_sh[0] < ema_sh[-1]:
            dir = "up"
        else:
            dir = ""
        #simple direction
        #trend, reversal
        trend = ""
        if ema_s >= ema_l + atr:
            trend = "bullish"
        elif ema_s <= ema_l - atr:
            trend = "bearish"
#         else:
#             trend = ""
        t_rev = False
        if self.trend != trend:
            t_rev = True
            self.trend = trend
        #trend, reversal
        #trend crossover signaling
        trend_signal = ""
        if t_rev:
            #acts only on bearish crossover rn.
            if trend == "bearish":
                trend_signal = "sell"
            elif trend == "bullish":
                trend_signal = "buy"
        #trend crossover signaling
        
        ######support/resistance zone handling###########
        log.debug ("*******%d:(%s) zone_s: %s zone_r: %s vwap: %f rsi: %f atr: %f cur_close: %f"%(cdl.time,
            dt.time(), self.s_l, self.r_l, vwap, rsi, atr, cur_close))
        za = ""        
        if dir == "up":
            #see if we are near any resistance zones or crossed
            try:
                i = 0
                while True:
                    r, w = self.r_l.peekitem(i)
                    #czse 1. moving up from resistance
                    if cur_close >= r + (w + self.atr_mx)*atr:
                        #resistance crossed, flip roles - resistance becomes support now
                        log.debug ("TATS - broke resistance %f: %d cur_close: %f"%(r, w, cur_close))                    
                        self.s_l[r] = 0
                        del(self.r_l[r])                   
                        if za == "":
                            #cases where we broke one res and in the zone of other, don't buy (conservative buy)
                            za = "buy"
                            self.res_try_break = False
    #                     break #could we break multiple resistance in one candle? yes!
                    elif cur_close >= r - ( self.atr_mx)*atr:
                        #case 2: trying to break resistance. within the range now.
                        log.debug ("TATS - trying to break resistance %f: %d cur_close: %f"%(r, w, cur_close))
                        if self.res_try_break == False:
                            #count the res zone entry
                            self.res_try_break = True 
                        #cases where we broke one res and in the zone of other, don't buy (conservative buy)                        
                        za = "hold"
                        i+=1
                    else:
                        #not in zones
                        break
            except:
                #r_list empty, or traversed all list
                pass

            #case3: check if we are in vwap resistance zone
            if cur_close >= vwap + self.atr_mx*atr:
                if self.vwap_try_break == True:
                    #broke VWAP resistance, new break
                    log.debug ("TATS - broke vwap(%f) resistance BUY "%(vwap))                    
                    if za == "":
                        self.vwap_try_break = False
                        za = "buy"
            elif cur_close >= vwap - self.atr_mx*atr:
                log.debug ("TATS - trying to break VWAP resistance %f"%(vwap))                
                self.vwap_try_break = True
                za = "hold"             
            #case 4. moving up from support, see if we are out of zone
            if self.sup_try_break == True:
                s, w = self.s_l.peekitem()
                if cur_close >= s + (w + self.atr_mx)*atr:
                    #out of support range, we might go up now
                    if za == "":
                        #couldn't break support zone, makes support stronger
                        log.debug ("TATS - unable to break support, BUY ")                                            
                        self.s_l[s] = w+1                        
                        self.sup_try_break = False             
                        za = "buy"    
        elif dir == "down":
            #see if we are near any support zones or crossed
            try:
                i = -1
                while True:
                    s, w = self.s_l.peekitem(i)
                    #case 1: support broke. we might go down further. sell. 
                    if cur_close <= s - (w + self.atr_mx)*atr:
                        #support broke, flip roles
                        log.debug ("TATS - broke support %f: %d cur_close: %f"%(s, w, cur_close))                    
                        self.r_l[s] = 0
                        del(self.s_l[s])                   
                        za = "sell"
                        self.sup_try_break = False
                    elif cur_close <= s + (self.atr_mx)*atr:
                        #case 2: trying to break support. within the range now.
                        log.debug ("TATS - trying to break support %f: %d cur_close: %f"%(s, w, cur_close))
                        if self.sup_try_break == False:
                            #count the sup zone entry
                            self.sup_try_break = True 
                        if za == "":
                            za = "hold"
                        i-=1
                    else:
                        #not in zones
                        break
            except:
                #s_list empty, or traversed all list
                pass
            #check if we are in vwap support range
            if cur_close <= vwap - self.atr_mx*atr:
                if self.vwap_try_break == True:
                #broke VWAP support, new break from range
                    self.vwap_try_break = False
                    za = "sell"
                    log.debug ("TATS - SELL vwap(%f) support broke cur_close: %f "%(vwap, cur_close))                
            elif cur_close <= vwap + self.atr_mx*atr:
                self.vwap_try_break = True
                if za == "":                
                    za = "hold"
                    log.debug ("TATS - HOLD vwap(%f) support range cur_close: %f "%(vwap, cur_close))                    
            #case 2: tried break resistance and failed. we could go further down. sell
            if self.res_try_break == True:
                r, w = self.r_l.peekitem(0)
                if cur_close <= r - (w + self.atr_mx)*atr:
                    #out of resistance range, we might go down further
                    if za == "":
                        #couldn't break resistance zone, makes reistance stronger
                        log.debug ("TATS - unable to break resistance, SELL ")                        
                        self.r_l[r] = w+1                        
                        self.res_try_break = False             
                        za = "sell"
        if za != "":
            #there is a new state else maintain previous state
            log.debug (" -- >new zone action :%s < --"%(za))
            self.zone_action = za                       
        ######support/resistance zone handling###########
        
        ####### RSI/MFI signaling ########
        if rsi > self.rsi_overbought:
            self.rsi_trend = "OB"
        elif rsi < self.rsi_oversold:
            self.rsi_trend = "OS"
        else:   #elif rsi >= 30 and rsi <= 60:
            self.rsi_trend = ""
        
        if (self.rsi_trend == "OS" and 
            all(mfi_l[i] <= mfi_l[i+1] for i in range(len(mfi_l)-1)) and 
            all(rsi_l[i] <= rsi_l[i+1] for i in range(len(rsi_l)-1))):
            #recovering
            log.debug("TATS - recovering from oversold(%f). BUY"%(rsi))
            self.rsi_action = "buy"
        elif (self.rsi_trend == "OB" and 
              all(mfi_l[i] >= mfi_l[i+1] for i in range(len(mfi_l)-1)) and 
              all(rsi_l[i] >= rsi_l[i+1] for i in range(len(rsi_l)-1))):
            log.debug("TATS - overbought(%f) SELL"%(rsi))            
            self.rsi_action = "sell"
        ####### RSI/MFI signaling ########

        if self.rsi_action == "buy" and (self.zone_action == "buy" or self.zone_action == ""):
            #conservative buy
            log.debug (" >>>>>>>>>>>>>>>>> BUY z_a: %s rsi_a: %s"%(self.zone_action, self.rsi_action))            
            signal = 1
            self.rsi_action = self.zone_action = ""
        elif  self.rsi_action == "sell" or self.zone_action == "sell" or trend_signal == "sell":
            #proactive sell
            log.debug (" >>>>>>>>>>>>>>>> SELL z_a: %s rsi_a: %s trend_signal: %s"%(self.zone_action, self.rsi_action, trend_signal))            
            signal = -1
            self.rsi_action = self.zone_action = ""
        log.debug ("cdl time; %d opentime: %d %d "%(cdl.time , self.open_time + 30*60, self.close_time))
        if (cdl.time < self.open_time + self.open_delay*60) or (cdl.time > self.close_time - (self.close_delay+10)*60):
            #let's not buy anything within half n hr of market open and sell everything 15min in to market close
            # don't buy if we are with in 10mins of close delay window below
            log.debug ("TATS - open delay skip trade signal: %d"%(signal))      
            signal = 0
        elif cdl.time > self.close_time - self.close_delay*60:
            # we are a day trading strategy and let's not carry over to next day            
            log.debug ("TATS - closing day window. SELL everything signal: %d"%(signal))
            signal = -1
            
        return signal
    
# EOF
