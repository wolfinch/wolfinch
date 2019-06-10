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
from indicators.ta_ema import EMA
from indicators.ta_trix import TRIX
from indicators.bollinger import BBANDS
from indicators.adx import ADX
from indicators.cci import CCI
from indicators.rsi import RSI
from indicators.sar import SAR
from indicators.macd import MACD
from indicators import indicator

market_indicators = []
init_done = False

indicators_list = {
    "close": NOOP,
    "SMA": SMA,
    "EMA": EMA,
    "TRIX": TRIX,
    "BBANDS": BBANDS,
    "ADX": ADX,
    "CCI": CCI,
    "RSI": RSI,
    "SAR": SAR,
    "MACD": MACD
    }

def Configure (config_list):
    global init_done, market_indicators, indicators_list
    #### Configure the Strategies below ######
    
    if init_done:
        return market_indicators
    
    if not len(config_list):
        print("no indicators to be configured!! potentially no active strategies!")
        raise ("no indicators to be configured!! potentially no active strategies!")
    
    
    for ind_name, period_list in config_list.iteritems():
        indicator = indicators_list.get (ind_name)
        if not indicator:
            print ("Invalid Indicator(%s)! Either indicator not available, or unable to configure"%(ind_name))
            raise ("Invalid Indicator(%s)! Either indicator not available, or unable to configure"%(ind_name))
        if not len(period_list):
            #default/non-period based indicator
            market_indicators.append(indicator(ind_name))
        else:
            for period in period_list:
                market_indicators.append(indicator("%s%d"%(ind_name, period), period))
                    
        
#     # No-Op. To get Close price
#     noop = NOOP ('close')
#     
#     # SMA15, SMA50
#     sma15 = SMA ('SMA15', 15)
#     sma50 = SMA ('SMA50', 50)
#         
#     #TA_EMA12, TA_EMA26
#     ta_ema5 = EMA ('EMA5', 5)
#     ta_ema13 = EMA ('EMA13', 13)    
#     ta_ema21 = EMA ('EMA21', 21)
#     ta_ema80 = EMA ('EMA80', 80)
#     ta_ema50 = EMA ('EMA50', 50)
#     ta_ema120 = EMA ('EMA120', 120)
#         
#     #TA_TRIX30
#     ta_trix30 = TRIX ('TRIX30', 30)    
#             
#     bbands = BBANDS ('BBANDS') # Bollinger Bands
#     adx = ADX('ADX') #Average Directional Movement Index (Momentum Indicators)
#     cci = CCI('CCI')
#     rsi14 = RSI('RSI14', 14)
#     rsi21 = RSI('RSI21', 21)    
#     sar = SAR('SAR')
#     macd = MACD('MACD')
#             
#     # List of all the available strategies
#     market_indicators = [
#             noop,
#             sma15,
#             sma50,
#             #ema12,
#             #ema26,
#             ta_ema5,
#             ta_ema13,
#             ta_ema21,
#             ta_ema80,
#             ta_ema50,
#             ta_ema120, 
#             bbands,
#             adx,        # FIXME: bug
#             cci,
#             rsi14,
#             rsi21,
#             sar,
#             macd,
#             ta_trix30
#         ]
    
    #### Configure the Strategies - end ######
    init_done = True
    return market_indicators

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Indicators Test")
    Configure ()
    
    
#EOF