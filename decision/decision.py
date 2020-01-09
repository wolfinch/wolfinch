# Wolfinch Auto trading Bot
# Desc: Decision engine
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

from utils import getLogger
from . import decision_simple
# import decision_ML

log = getLogger ('DECISION')
log.setLevel(log.CRITICAL)

# g_decision_type = "simple"
# g_decision_config = None
g_strategy_list = {}

class Decision ():
    def __init__(self, market, market_list, decision_type, config):        
        log.debug ("init decision for market(%s): model:%s config: %s"%(market.name, decision_type, config))
        if decision_type == "simple":
            strategy = config.get("strategy")
            params = config.get("params")
            if strategy == None:
                log.critical ("Strategy not configured")
                raise ("Strategy not configured")            
            self.decision = decision_simple.Decision(market, market_list, config={strategy: params})
        elif  decision_type == "ml":
            self.decision = decision_ML.Decision(market, market_list, config_path=config)
        else:
            log.error ("Unknown decision type %s"%(decision_type))
            return None    
            
    def generate_signal(self, idx):
        return self.decision.generate_signal(idx)
         
    def summary(self):
        pass
    
# setup decision related configs and states based on global_config
def decision_config (exchange_name, product_id, decision_type, config):
#     global g_decision_type, g_decision_config, 
    global g_strategy_list
    
    if str(decision_type).lower() == "simple":
        log.info ("decision simple config: %s "%(config))
#         g_decision_type = "simple"
#         g_decision_config = config
        # TODO: TBD: add support for multiple strategies
        strategy = config.get("strategy")
        if strategy == None:
            log.critical ("Strategy not configured")
            raise ("Strategy not configured")
        if not g_strategy_list.get(exchange_name):
            g_strategy_list[exchange_name] = {product_id:{}}
        elif not g_strategy_list[exchange_name].get (product_id):
            g_strategy_list[exchange_name][product_id] = {}
            
        g_strategy_list[exchange_name][product_id][strategy] =   config['params']
    elif str(decision_type).lower() == "ml":
        log.info ("decision ML")
#         g_decision_type = "ml"
#         g_decision_config = config
    else:
        log.critical ("Unsupported decision type(%s) cfg:%s"%(decision_type, str(config)))
        raise "Unsupported decision type(%s) cfg:%s"
        
def get_strategy_list(exchange_name, product_id):
    global g_strategy_list
    return g_strategy_list[exchange_name][product_id]

#EOF
