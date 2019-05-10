# OldMonk Auto trading Bot
# Desc: ML based decision engine impl
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
from models.model_simple_DAE import Model, load_model
# from models.model_LSTM import Model
# from models.model_SVC import Model

log = getLogger ('decision_simple')
log.setLevel(log.DEBUG)

class Decision ():
    def __init__(self, market, market_list, config_path="", **kwargs):        
        log.debug ("init decision for market(%s)"%(market.name))
        
        if config_path == "":
            log.critical("Unable to load pretrained model. Invalid cfg_path")
            return None
        else:
            self.model = load_model(config_path)
            if self.model == None:
                log.critical("Unable to load pretrained model.")
                return None                
        self.market = market
        self.market_list = market_list
                        
    def generate_signal(self, idx):
        # simple decision uses the latest "EMA_RSI" strategy signal for now
        
        #TODO: FIXME: jork: add logic for normalizing data and call predict
        return self.model.predict(idx)
         
    def summary(self):
        pass
    
#EOF