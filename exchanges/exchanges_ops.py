'''
 OldMonk Auto trading Bot
 Desc: Exchanges list 
         All exchange housekeeping ops here
 (c) OldMonk Bot
'''

from utils import getLogger
from exchanges_config import all_exchanges

__name__ = "EXCH-OPS"
log = getLogger (__name__)
log.setLevel (log.INFO)


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