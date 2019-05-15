# OldMonk Auto trading Bot
# Desc: Simple decision policy impl
# 
# Copyright 2018, Joshith Rayaroth Koderi. All Rights Reserved.
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

from utils import getLogger

log = getLogger ('decision_simple')
log.setLevel(log.CRITICAL)

class Decision ():
    num_dec = 0
    def __init__(self, market, market_list, *args):        
        log.debug ("init decision for market(%s)"%(market.name))
        self.market = market
        self.market_list = market_list
                
    def generate_signal(self, idx):

        # simple decision uses the latest "EMA_RSI" strategy signal for now
        return self.market.market_strategies_data[idx]["EMA_RSI"]#["TREND_RSI"] 
#         signal = min (self.market.market_strategies_data[idx]["EMA_RSI"],
#                        self.market.market_strategies_data[idx]["TREND_RSI"] )
#         
#         if signal < 0:
#             signal = max (self.market.market_strategies_data[idx]["EMA_RSI"],
#                        self.market.market_strategies_data[idx]["TREND_RSI"] )
        
#         if signal != 0:
#             if self.num_dec > 5 :
#                 return 0
#             else:
#                 self.num_dec += 1        
            
#         return signal
         
    def summary(self):
        pass
    
#EOF