#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc:  Global Market Indicators Configuration. 
# ref. implementation.
# All the globally available market Indicators are instantiated and configured here.
# If a market specific Indicators list is required, a similar config may be made specific to the market
# Copyright 2018, Joshith Rayaroth Koderi. All Rights Reserved.
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
from indicators.ema import EMA
from indicators.ta_ema import TA_EMA
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
    noop = NOOP ('closing')
    
    # SMA15, SMA50
    sma15 = SMA ('sma15', 15)
    sma50 = SMA ('sma50', 50)
    
    #EMA12, EMA26
    ema12 = EMA ('ema12', 12)
    ema26 = EMA ('ema26', 26)
        
    #TA_EMA12, TA_EMA26
    ta_ema12 = TA_EMA ('ta_ema12', 12)
    ta_ema26 = TA_EMA ('ta_ema26', 26)
            
    bbands = BBANDS ('bbands') # Bollinger Bands
    adx = ADX('adx') #Average Directional Movement Index (Momentum Indicators)
    cci = CCI('cci')
    rsi = RSI('rsi')
    sar = SAR('sar')
    macd = MACD('macd')
            
    # List of all the available strategies
    global market_indicators
    market_indicators = [
            noop,
            sma15,
            sma50,
            #ema12,
            #ema26,
            ta_ema12,
            ta_ema26,
            bbands,
            adx,        # FIXME: bug
            cci,
            rsi,
            sar,
            macd
        ]
    
    #### Configure the Strategies - end ######
    init_done = True
    return market_indicators

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Indicators Test")
    Configure ()
    
    
#EOF