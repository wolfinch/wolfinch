#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc:  Global Market Indicators Configuration. 
# ref. implementation.
# All the globally available market Indicators are instantiated and configured here.
# If a market specific Indicators list is required, a similar config may be made specific to the market
# Copyright 2018, OldMonk Bot. All Rights Reserved.
#
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

from indicators.noop import NOOP
from indicators.sma import SMA
# from indicators.ema import EMA
from indicators.ta_ema import TA_EMA
from indicators.ta_trix import TA_TRIX
from indicators.bollinger import BBANDS
from indicators.adx import ADX
from indicators.cci import CCI
from indicators.rsi import RSI
from indicators.sar import SAR
from indicators.macd import MACD

market_indicators = []
init_done = False

def Configure ():
    global init_done, market_indicators
    #### Configure the Strategies below ######
    
    if init_done:
        return market_indicators
    
    # No-Op. To get Close price
    noop = NOOP ('close')
    
    # SMA15, SMA50
    sma15 = SMA ('SMA15', 15)
    sma50 = SMA ('SMA50', 50)
    
    #EMA12, EMA26
    #ema12 = EMA ('EMA12', 12)
    #ema26 = EMA ('EMA26', 26)
        
    #TA_EMA12, TA_EMA26
    ta_ema5 = TA_EMA ('EMA5', 5)
    ta_ema13 = TA_EMA ('EMA13', 13)    
    ta_ema21 = TA_EMA ('EMA21', 21)
    ta_ema80 = TA_EMA ('EMA80', 80)
    ta_ema50 = TA_EMA ('EMA50', 50)
    ta_ema120 = TA_EMA ('EMA120', 120)
        
    #TA_TRIX30
    ta_trix30 = TA_TRIX ('TRIX30', 30)    
            
    bbands = BBANDS ('BBANDS') # Bollinger Bands
    adx = ADX('ADX') #Average Directional Movement Index (Momentum Indicators)
    cci = CCI('CCI')
    rsi14 = RSI('RSI14', 14)
    rsi21 = RSI('RSI21', 21)    
    sar = SAR('SAR')
    macd = MACD('MACD')
            
    # List of all the available strategies
    market_indicators = [
            noop,
            sma15,
            sma50,
            #ema12,
            #ema26,
            ta_ema5,
            ta_ema13,
            ta_ema21,
            ta_ema80,
            ta_ema50,
            ta_ema120, 
            bbands,
            adx,        # FIXME: bug
            cci,
            rsi14,
            rsi21,
            sar,
            macd,
            ta_trix30
        ]
    
    #### Configure the Strategies - end ######
    init_done = True
    return market_indicators

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Indicators Test")
    Configure ()
    
    
#EOF