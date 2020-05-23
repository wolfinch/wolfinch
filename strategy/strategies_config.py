#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: Global Market Strategy Configuration. 
# ref. implementation.
# All the globally available market strategies are instantiated and configured here.
# If a market specific strategy list is required, a similar config may be made specific to the market
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

#### List all available strategies below ###
strategies_list = {
    "TREND_RSI"         : "trend_rsi",
    "EMA_RSI"           : "ema_rsi",
    "EMA_RSI_SLOW"      : "ema_rsi_slow",    
    "EMA_DEV"           : "ema_dev",
    "TREND_BOLLINGER"   : "trend_bollinger",
    "TRIX_RSI"          : "trix_rsi",
    "MINMAX"            : "minmax",
    "TRABOS"            : "trabos",
    "TATS"              : "tats"
    }
#### List all available strategies above ###

#EOF
