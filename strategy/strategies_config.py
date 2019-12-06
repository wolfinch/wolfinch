#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: Global Market Strategy Configuration. 
# ref. implementation.
# All the globally available market strategies are instantiated and configured here.
# If a market specific strategy list is required, a similar config may be made specific to the market
#
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

from strategies.trend_rsi import TREND_RSI
from strategies.ema_rsi import EMA_RSI
from strategies.ema_rsi_slow import EMA_RSI_SLOW
from strategies.ema_dev import EMA_DEV
from strategies.trend_bollinger import TREND_BOLLINGER
from strategies.trix_rsi import TRIX_RSI
from strategies.minmax import MINMAX


#### List all available strategies below ###
strategies_list = {
    "TREND_RSI": TREND_RSI,
    "EMA_RSI": EMA_RSI,
    "EMA_RSI_SLOW": EMA_RSI_SLOW,    
    "EMA_DEV": EMA_DEV,
    "TREND_BOLLINGER": TREND_BOLLINGER,
    "TRIX_RSI": TRIX_RSI,
    "MINMAX": MINMAX
    }
#### List all available strategies above ###

#EOF
