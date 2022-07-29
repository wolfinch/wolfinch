# Wolfinch Auto trading Bot
# Desc: Simple decision policy impl
#
#  Copyright: (c) 2017-2022 Wolfinch Inc.
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

log = getLogger ('decision_simple')
log.setLevel(log.CRITICAL)

class Decision ():
    num_dec = 0
    def __init__(self, market, market_list, config=None):        
        log.debug ("init decision for market(%s) config: %s"%(market.name, str(config)))
        
        if config == None:
            log.critical("strategy not configured for simple decision")
            raise ("strategy not configured for simple decision")
        
        for strategy in config.keys():
            self.strategy = strategy
            ##TODO: TBD: do we need to support multi strategies here?? for now not supported
            break
    
        self.market = market
        self.market_list = market_list
                
    def generate_signal(self, idx):
        d = self.market.market_strategies_data[idx][self.strategy]
        if type(d) == tuple:
            # strategy provides signal, SL, TP
            return d[0], d[1], d[2]
        return d, 0, 0
         
    def summary(self):
        pass
    
#EOF
