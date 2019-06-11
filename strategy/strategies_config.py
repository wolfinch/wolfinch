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

from strategies.trend_rsi import TREND_RSI
from strategies.ema_rsi import EMA_RSI
from strategies.ema_dev import EMA_DEV
from strategies.trend_bollinger import TREND_BOLLINGER
from strategies.trix_rsi import TRIX_RSI
from strategies.minmax import MINMAX


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

#EOF