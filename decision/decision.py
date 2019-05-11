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
import decision_simple
# import decision_ML

log = getLogger ('DECISION')
log.setLevel(log.DEBUG)

class Decision ():
    def __init__(self, market, market_list, decision_type="", config_path=""):        
        log.debug ("init decision for market(%s): model:%s config_path: %s"%(market.name, decision_type, config_path))
        if str(decision_type).lower() == "simple":
            self.decision = decision_simple.Decision(market, market_list)
        elif str(decision_type).lower() == "ml":
            self.decision = decision_ML.Decision(market, market_list, config_path=config_path)
        else:
            log.error ("Unknown decision type %s"%(decision_type))
            return None    
            
    def generate_signal(self, idx):
        return self.decision.generate_signal(idx)
         
    def summary(self):
        pass
    
#EOF