'''
 OldMonk Auto trading Bot
 Desc: Exchanges list 
         All exchange housekeeping ops here
 (c) OldMonk Bot
'''

from utils import getLogger
from exchanges_config import all_exchanges
import sims

__name__ = "EXCH-OPS"
log = getLogger (__name__)
log.setLevel (log.CRITICAL)


exchange_list = []
def init_exchanges (OldMonkConfig):
    global exchange_list
    

    #init exchanges 
    for exch_cls in all_exchanges:
        log.debug ("Initializing exchange (%s)"%(exch_cls.name))
        for exch in OldMonkConfig['exchanges']:
            for name,v in exch.iteritems():
                if name.lower() == exch_cls.name.lower():
                    role = v['role']
                    cfg = v['config']
                    log.debug ("initializing exchange(%s)"%name)
                    if (sims.simulator_on):
                        # If sim is on, init only sim exchange
                        exch_obj = sims.SIM_EXCH(exch_cls.name)
                        log.info ("SIM-EXCH initialized for EXCH(%s)"%(exch_cls.name))                        
                    else:                    
                        exch_obj = exch_cls(config=cfg, primary=(role == 'primary'))
                    if (exch_obj != None):
                        exchange_list.append(exch_obj)
                        #Market init
                    else:
                        log.critical (" Exchange \"%s\" init failed "%exch_cls.name)
                
def close_exchanges():
    global exchange_list
    #init exchanges 
    for exchange in exchange_list:
            log.info ("Closing exchange (%s)"%(exchange.name))
            exchange.close()    



                    
#EOF    