#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc:  Global Market Indicators Configuration. 
# ref. implementation.
# All the globally available market Indicators are instantiated and configured here.
# If a market specific Indicators list is required, a similar config may be made specific to the market
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

import importlib
from indicators import indicator

market_indicators = {}
# init_done = False

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
    global init_done, market_indicators
    #### Configure the Strategies below ######
    
#     if init_done:
#         return market_indicators[exchange_name][product_id]
    
    if not len(config_list):
        print("no indicators to be configured!! potentially no active strategies!")
        raise ("no indicators to be configured!! potentially no active strategies!")
    
    
    for ind_name, period_list in config_list.items():
        indicator = get_indicator_by_name (ind_name)
        if not indicator:
            errstr = "Invalid Indicator(%s)! Either indicator not available, or unable to configure"%(ind_name)
            print (errstr)
            raise Exception(errstr)
        if not market_indicators.get (exchange_name):
            market_indicators[exchange_name] = {product_id: []}
        elif not market_indicators[exchange_name].get(product_id):
            market_indicators[exchange_name][product_id] = []
        if not len(period_list):
            #default/non-period based indicator
            market_indicators[exchange_name][product_id].append(indicator(ind_name))
        else:
            for period in period_list:
                if type(period) == tuple:
                    #where indicator has more than one param to configure
                    market_indicators[exchange_name][product_id].append(indicator("%s%s"%(ind_name, str(period)), *period))
                else:
                    if period == 0:
                        market_indicators[exchange_name][product_id].append(indicator(ind_name))
                    else:
                        market_indicators[exchange_name][product_id].append(indicator("%s%s"%(ind_name, str(period)), period))
                    
    
    #### Configure the Strategies - end ######
#     init_done = True
    return market_indicators[exchange_name][product_id]

def get_indicator_by_name (name):
    return  import_indicator(name)

def import_indicator(ind_cls_name):
    strat_path = "indicators."+ind_cls_name.lower()
    try:
        mod = importlib.import_module(strat_path)
        return getattr(mod, ind_cls_name.upper(), None)
    except ModuleNotFoundError:
        return None

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Indicators Test")
    Configure ("SIM_EXCH", "BTC-USD", manual_indicator_config)
    
    
#EOF
