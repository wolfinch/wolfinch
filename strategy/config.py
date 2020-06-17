#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: Global Market Strategy Configuration. 
# ref. implementation.
# All the globally available market strategies are instantiated and configured here.
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

import importlib

import indicators

init_done = False

market_strategies = {}


def Configure (exchange_name, product_id, strategy_list={}):
    global init_done, market_strategies
#     if init_done:
#         return market_strategies[exchange_name][product_id]
    #### Configure the Strategies below ######
    
    if not len(strategy_list):
        if market_strategies.get(exchange_name):
            return market_strategies[exchange_name].get(product_id)
    
    for strategy_name, strategy_params in strategy_list.items():
        strategy = get_strategy_by_name(strategy_name)
        if not strategy:
            raise Exception("Unknown strategy(%s)" % (strategy_name))
        
        if not market_strategies.get(exchange_name):
            market_strategies[exchange_name] = {product_id :[]}
        elif not market_strategies[exchange_name].get (product_id):
            market_strategies[exchange_name][product_id] = []
            
        if strategy_params:
            market_strategies[exchange_name][product_id].append(strategy(strategy_name, **strategy_params))
        else:
            market_strategies[exchange_name][product_id].append(strategy(strategy_name))            
    
    #### Configure the Strategies - end ######
#     init_done = True
    return market_strategies[exchange_name][product_id]


def Configure_indicators(exchange_name, product_id, ext_indicators = None):
    global market_strategies
    # _indicator_list var in abstract class is a central place for all reqd. indicators
    if not len(market_strategies):
        print ("no strategies configured!!")
        raise ("no strategies configured!!")
    req_indicators = gen_product_indicators_list (exchange_name, product_id)
    if ext_indicators:
        for key in ext_indicators:
            if req_indicators.get (key):
                req_indicators[key].update(ext_indicators[key])
            else:
                req_indicators[key] = ext_indicators[key]
    return indicators.Configure(exchange_name, product_id, req_indicators)


def gen_product_indicators_list (exchange_name, product_id):
    global market_strategies
    strat_list = market_strategies[exchange_name][product_id]
    ind_list = {}
    for strat in strat_list:
        inds = strat.get_indicators()
        for ind_name in inds.keys():
            ind_periods = inds[ind_name]
            ind = ind_list.get(ind_name, None)
            if ind:
                ind.update(ind_periods)
            else:
                ind_list[ind_name] = set(ind_periods)
    return ind_list

def get_strategy_by_name (name):
    return  import_strategy(name)

def import_strategy(strat_cls_name):
    strat_path = "strategy.strategies."+strat_cls_name.lower()
    try:
        mod = importlib.import_module(strat_path)
        return getattr(mod, strat_cls_name.upper(), None)
    except ModuleNotFoundError as e:
        print("error loading module - %s"%(str(e)))
        raise e

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Strategy Test.")
    Configure("CBPRO", "BTC-USD", {"EMA_DEV": {}})
    Configure_indicators("CBPRO", "BTC-USD")
    Configure("CBPRO", "XLM-USD", {"EMA_RSI": {'rsi_bullish_mark': 36, 'rsi': 14, 'ema_s': 84}})
    Configure_indicators("CBPRO", "XLM-USD")    
    print ("Strategy config success: all indicators: %s" % (str(gen_product_indicators_list("CBPRO", "XLM-USD"))))
    print ("Strategy config success: all indicators: %s" % (str(gen_product_indicators_list("CBPRO", "BTC-USD"))))
    
# EOF
