#! /usr/bin/env python
#
# OldMonk Auto trading Bot
# Desc: Global Market Strategy Configuration. 
# ref. implementation.
# All the globally available market strategies are instantiated and configured here.
# If a market specific strategy list is required, a similar config may be made specific to the market
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

from trend_rsi import TREND_RSI
from ema_rsi import EMA_RSI
from ema_dev import EMA_DEV
from trend_bollinger import TREND_BOLLINGER
from trix_rsi import TRIX_RSI
from minmax import MINMAX

init_done = False


#### List all available strategies below ###
strategies_list = {
    "TREND_RSI": TREND_RSI,
    "EMA_RSI": EMA_RSI,
    "EMA_DEV": EMA_DEV,
    "TREND_BOLLINGER": TREND_BOLLINGER,
    "TRIX_RSI": TRIX_RSI,
    "MINMAX": MINMAX
    }
#### List all available strategies above ###

market_strategies = []
def Configure (strategy_list={}):
    global init_done, market_strategies, strategies_list
    if init_done:
        return market_strategies
    #### Configure the Strategies below ######
    
    if not len(strategy_list):
        return market_strategies
    
    for strategy_name, strategy_params in strategy_list.iteritems():
        strategy = strategies_list.get(strategy_name)
        if not strategy:
            raise ("Unknown strategy(%s)"%(strategy_name))
        market_strategies.append(strategy(strategy_name, **strategy_params))
    
    #### Configure the Strategies - end ######
    init_done = True
    return market_strategies

def Configure_indicators():
    global market_strategies
    #_indicator_list var in abstract class is a central place for all reqd. indicators
    if not len(market_strategies):
        print ("no strategies configured!!")
        raise ("no strategies configured!!")
    req_indicators = market_strategies[-1]._indicator_list
    return indicators.Configure(req_indicators)

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Strategy Test.")
    Configure()
    Configure_indicators()
    print ("Strategy config success: all indicators: %s"%(str(market_strategies[-1]._indicator_list)))
    
#EOF