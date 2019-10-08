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

market_indicators = {}
# init_done = False

#Configure all the available indicators here:
# only the indicators required for enabled strategy will be enforced.
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

# Manually configure all required indicators. Should be used with auto-generation strategy 
manual_indicator_config = {
    'close': {},
    'SMA' : {15, 50},
    'EMA': {80, 50, 5, 120, 13, 21},    
    'BBANDS': {},
    'TRIX' : {30},
    'ADX' : {},
    'CCI' : {},
    'SAR' : {},
    'MACD': {},
    'RSI': {21, 14},
    'TRIX': {30},
    }

def Configure (exchange_name, product_id, config_list):
    global init_done, market_indicators, indicators_list
    #### Configure the Strategies below ######
    
#     if init_done:
#         return market_indicators[exchange_name][product_id]
    
    if not len(config_list):
        print("no indicators to be configured!! potentially no active strategies!")
        raise ("no indicators to be configured!! potentially no active strategies!")
    
    
    for ind_name, period_list in config_list.iteritems():
        indicator = indicators_list.get (ind_name)
        if not indicator:
            print ("Invalid Indicator(%s)! Either indicator not available, or unable to configure"%(ind_name))
            raise ("Invalid Indicator(%s)! Either indicator not available, or unable to configure"%(ind_name))
        if not market_indicators.get (exchange_name):
            market_indicators[exchange_name] = {product_id: []}
        elif not market_indicators[exchange_name].get(product_id):
            market_indicators[exchange_name][product_id] = []
        if not len(period_list):
            #default/non-period based indicator
            market_indicators[exchange_name][product_id].append(indicator(ind_name))
        else:
            for period in period_list:
                market_indicators[exchange_name][product_id].append(indicator("%s%d"%(ind_name, period), period))
                    
    
    #### Configure the Strategies - end ######
#     init_done = True
    return market_indicators[exchange_name][product_id]

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Indicators Test")
    Configure ("SIM_EXCH", "BTC-USD", manual_indicator_config)
    
    
#EOF
