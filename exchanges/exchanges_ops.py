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
    for exch_cls in all_exchanges:
        log.debug ("Initializing exchange (%s)"%(exch_cls.name))
        for exch in WolfinchConfig['exchanges']:
            for name, exch_cfg in exch.items():
                if name.lower() == exch_cls.name.lower():
                    role = exch_cfg['role']
#                     cfg = exch_cfg['config']
                    log.debug ("initializing exchange(%s)"%name)
                    if (sims.simulator_on):
                        sims.exch_obj = sims.SIM_EXCH(exch_cls.name)
                        log.info ("SIM-EXCH initialized for EXCH(%s)"%(exch_cls.name))
                        if sims.backtesting_on:
                            # If backtesting is on, init only sim exchange
                            # do a best effort setup for products for sim/backtesting based on config.
                            sims.exch_obj.setup_products(exch_cfg["products"])
                            if (sims.exch_obj != None):
                                exchange_list.append(sims.exch_obj)
                                #Market init
                                log.info ("Backtesting_on! skip real exch init!")                                
                                return
                            else:
                                log.critical (" Exchange \"%s\" init failed "%exch_cls.name)
                                raise Exception()
                    exch_obj = exch_cls(config=exch_cfg, primary=(role == 'primary'))
                    if (exch_obj != None):
                        exchange_list.append(exch_obj)
                    if sims.simulator_on:
                        #add initialized products for sim. We can do this only here after real exch initialized products
                        log.info("sim exch products init for exch:%s"%(name))
                        sims.exch_obj.add_products(exch_obj.get_products())
                    else:
                        log.critical (" Exchange \"%s\" init failed "%exch_cls.name)
                        raise Exception()
def close_exchanges():
    global exchange_list
    #init exchanges 
    for exchange in exchange_list:
            log.info ("Closing exchange (%s)"%(exchange.name))
            exchange.close()    



                    
#EOF    
