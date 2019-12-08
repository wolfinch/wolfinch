# Wolfinch Auto trading Bot
# Desc: ML based decision engine impl
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

from utils import getLogger
from .models.model_simple_DAE import Model, load_model
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
