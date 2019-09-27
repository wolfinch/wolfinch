#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Global Market Strategy Configuration. 
# ref. implementation.
# All the globally available market strategies are instantiated and configured here.
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

import indicators
from strategies_config import strategies_list

init_done = False

market_strategies = {}


def Configure (exchange_name, product_id, strategy_list={}):
    global init_done, market_strategies
    if init_done:
        return market_strategies[exchange_name][product_id]
    #### Configure the Strategies below ######
    
    if not len(strategy_list):
        if market_strategies.get(exchange_name):
            return market_strategies[exchange_name].get(product_id)
    
    for strategy_name, strategy_params in strategy_list.iteritems():
        strategy = strategies_list.get(strategy_name)
        if not strategy:
            raise ("Unknown strategy(%s)" % (strategy_name))
        
        if not market_strategies.get(exchange_name):
            market_strategies[exchange_name] = {product_id :[]}
        elif not market_strategies[exchange_name].get (product_id):
            market_strategies[exchange_name][product_id] = []
            
        if strategy_params:
            market_strategies[exchange_name][product_id].append(strategy(strategy_name, **strategy_params))
        else:
            market_strategies[exchange_name][product_id].append(strategy(strategy_name))            
    
    #### Configure the Strategies - end ######
    init_done = True
    return market_strategies[exchange_name][product_id]


def Configure_indicators(exchange_name, product_id):
    global market_strategies
    # _indicator_list var in abstract class is a central place for all reqd. indicators
    if not len(market_strategies):
        print ("no strategies configured!!")
        raise ("no strategies configured!!")
    req_indicators = market_strategies[exchange_name][product_id][-1]._indicator_list
    return indicators.Configure(exchange_name, product_id, req_indicators)


def get_strategy_by_name (name):
    return  strategies_list.get(name, None)


######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Strategy Test.")
    Configure()
    Configure_indicators()
    print ("Strategy config success: all indicators: %s" % (str(market_strategies[-1]._indicator_list)))
    
# EOF
