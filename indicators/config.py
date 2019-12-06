#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc:  Global Market Indicators Configuration. 
# ref. implementation.
# All the globally available market Indicators are instantiated and configured here.
# If a market specific Indicators list is required, a similar config may be made specific to the market
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

from __future__ import print_function
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
