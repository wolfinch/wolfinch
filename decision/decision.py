# OldMonk Auto trading Bot
# Desc: Decision engine
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
import decision_simple as decision 

log = getLogger ('DECISION')
log.setLevel(log.DEBUG)

class Decision ():
    def __init__(self, market, market_list, model="", config_path=""):        
        log.debug ("init decision for market(%s): model:%s config_path: %s"%(market.name, model, config_path))
        self.decision = decision.Decision(market, market_list, model, config_path)        
            
    def generate_signal(self):
        return self.decision.generate_signal()
         
    def summary(self):
        pass
    
#EOF