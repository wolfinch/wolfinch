# OldMonk Auto trading Bot
# Desc: Simple decision policy impl
# 
# Copyright 2019, OldMonk Bot, Joshith Rayaroth Koderi. All Rights Reserved.
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
    def __init__(self, market, market_list, config=None):        
        log.debug ("init decision for market(%s) config: %s"%(market.name, str(config)))
        
        if config == None:
            log.critical("strategy not configured for simple decision")
            raise ("strategy not configured for simple decision")
        
        for strategy in config.iterkeys():
            self.strategy = strategy
            ##TODO: TBD: do we need to support multi strategies here?? for now not supported
            break
    
        self.market = market
        self.market_list = market_list
                
    def generate_signal(self, idx):
        return self.market.market_strategies_data[idx][self.strategy]
         
    def summary(self):
        pass
    
#EOF