'''
 Wolfinch Auto trading Bot
 Desc: Exchanges list 
         All exchange housekeeping ops here
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
'''

import importlib
from utils import getLogger
from .exchanges_config import all_exchanges
import sims

__name__ = "EXCH-OPS"
log = getLogger (__name__)
log.setLevel (log.INFO)


exchange_list = []
def init_exchanges (WolfinchConfig):
    global exchange_list
    
    #init exchanges 
    for exch_name, exch_cls_name in all_exchanges.items():
        log.debug ("Initializing exchange (%s:%s)"%(exch_name, exch_cls_name))
        for exch in WolfinchConfig['exchanges']:
            for name, exch_cfg in exch.items():
                if name.lower() == exch_name.lower():
                    role = exch_cfg['role']
#                     cfg = exch_cfg['config']
                    log.debug ("initializing exchange(%s)"%name)
                    exch_cls = import_exchange(exch_name, exch_cls_name)
                    if exch_cls == None:
                        log.critical("unable to initialize configured exchange (%s:%s)"%(exch_name, exch_cls_name))
                        return
                    if (sims.simulator_on):
                        sims.sim_obj["exch"] = sims.SIM_EXCH(exch_cls.name, exch_cfg)
                        # do a best effort setup for products for sim/backtesting based on config.
                        sims.sim_obj["exch"].setup_products(exch_cfg["products"])                        
                        log.info ("SIM-EXCH initialized for EXCH(%s)"%(exch_cls.name))
                        if sims.backtesting_on:
                            # If backtesting is on, init only sim exchange
                            if (sims.sim_obj["exch"] != None):
                                exchange_list.append(sims.sim_obj["exch"])
                                #Market init
                                log.info ("Backtesting_on! skip real exch init!")                                
                                return
                            else:
                                log.critical (" Exchange \"%s\" init failed "%exch_cls.name)
                                raise Exception()
                    exch_obj = exch_cls(config=exch_cfg, primary=(role == 'primary'))              
                    if (exch_obj != None):
                        exchange_list.append(exch_obj)
                    else:
                        log.critical (" Exchange \"%s\" init failed "%exch_cls.name)
                        raise Exception()
                    if sims.simulator_on:
                        #add initialized products for sim. We can do this only here after real exch initialized products
                        log.info("sim exch products init for exch:%s"%(name))
                        sims.sim_obj["exch"].add_products(exch_obj.get_products())       
def close_exchanges():
    global exchange_list
    #init exchanges 
    for exchange in exchange_list:
        log.info ("Closing exchange (%s)"%(exchange.name))
        exchange.close()

def import_exchange(exch_mod_name, exch_cls_name):
    log.info ("importing exch module: %s class: %s"%(exch_mod_name, exch_cls_name))
    exch_path = "exchanges."+exch_mod_name
    return getattr(importlib.import_module(exch_path), exch_cls_name, None)
#EOF    
