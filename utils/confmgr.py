#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: Main File implements Bot
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


from .readconf import readConf
from .logger import getLogger
import sims, ui

log = getLogger ('confmgr')
log.setLevel(log.INFO)
# Global Config 
WolfinchConfig = None
gDecisionConfig = {}
gTradingConfig = {"stop_loss_enabled": False,
                  "stop_loss_kind" : "simple",
                  "stop_loss_smart_rate": False,
                  "stop_loss_rate": 0,
                  "take_profit_enabled": False,
                  "take_profit_rate": 0}

def parse_product_config (cfg):
    global gDecisionConfig, gTradingConfig    
    parsed_tcfg = {}
    parsed_dcfg = {}    
    for k, v in cfg.items():
        if k == 'currency':
            parsed_tcfg ['currency'] = v
        if k == 'fund_max_liquidity':
            parsed_tcfg ['fund_max_liquidity'] = v
        if k == 'fund_max_per_buy_value':
            parsed_tcfg ['fund_max_per_buy_value'] = v
        if k == 'asset_max_per_trade_size':
            parsed_tcfg ['asset_max_per_trade_size'] = v
        if k == 'asset_min_per_trade_size':
            parsed_tcfg ['asset_min_per_trade_size'] = v
        if k == 'active':
            parsed_tcfg ['active'] = v        
        if k == 'stop_loss':
            for ex_k, ex_v in v.items():
                if ex_k == 'enabled':
                    parsed_tcfg ['stop_loss_enabled'] = ex_v
                elif ex_k == 'kind':
                    parsed_tcfg ['stop_loss_kind'] = ex_v
                    if ex_v not in ['simple', 'strategy']:        
                        parsed_tcfg ['stop_loss_smart_rate'] = True
                elif ex_k == 'rate':
                    parsed_tcfg ['stop_loss_rate'] = ex_v                    
        elif k == 'take_profit':
            for ex_k, ex_v in v.items():
                if ex_k == 'enabled':
                    parsed_tcfg ['take_profit_enabled'] = ex_v
                elif ex_k == 'rate':
                    parsed_tcfg ['take_profit_rate'] = ex_v                                    
        elif k == 'decision':
            for ex_k, ex_v in v.items():
                if ex_k == 'model':
                    parsed_dcfg ['model_type'] = ex_v
                elif ex_k == 'config':
                    parsed_dcfg ['model_config'] = ex_v
                    
    if not parsed_tcfg.get("take_profit") :
        if gTradingConfig.get("take_profit"):
            parsed_tcfg["take_profit"] = gTradingConfig.get("take_profit")
            
    if not parsed_tcfg.get("stop_loss") :
        if gTradingConfig.get("stop_loss"):
            parsed_tcfg["stop_loss"] = gTradingConfig.get("stop_loss")
                        
    if not parsed_dcfg.get("decision") :
        if gDecisionConfig.get("decision"):
            parsed_dcfg["decision"] = gDecisionConfig.get("decision")
                                    
    if ( not parsed_tcfg.get('fund_max_liquidity') or not parsed_tcfg.get('fund_max_per_buy_value') or 
         not parsed_tcfg.get('asset_min_per_trade_size')) :
        print ("trading config not set")
        raise Exception ("trading config not set")
    
    if parsed_tcfg.get('stop_loss_enabled', False) == False:
        parsed_tcfg ['stop_loss_enabled'] = False        
        parsed_tcfg ['stop_loss_smart_rate'] = False
    
    return parsed_tcfg, parsed_dcfg


def get_product_config (exch_name, prod_name):
    global WolfinchConfig
    
    log.debug ("get_config for exch: %s prod: %s" % (exch_name, prod_name))
        
    # sanitize the config
    for k, v in WolfinchConfig.items():
        if k == 'exchanges':
            if v == None:
                log.critical ("Atleast one exchange need to be configured")
                raise Exception("exchanges not configured")
            for exch in v:
                for ex_k, ex_v in exch.items():
                    if ex_k.lower() != exch_name.lower():
                        continue
                    log.debug ("processing exch: %s val:%s" % (ex_k, ex_v))
                    products = ex_v.get('products')
                    if products != None and len(products):
                        log.debug ("processing exch products")
                        for prod in products:
                            for p_name, p_cfg in prod.items():
                                if p_name.lower() != prod_name.lower():
                                    continue
                                log.debug ("processing product %s:" % (p_name))
                                tcfg, dcfg = parse_product_config(p_cfg)
                                
                                #get fee, market_type
                                fee = ex_v.get('fee')
                                if not fee :
                                    print ("exchange fee not set")
                                    raise Exception("exchange fee not set")
                                order_type = ex_v.get('order_type')
                                if not order_type :
                                    print ("exchange order_type not set")
                                    raise Exception("exchange order_type not set")
                                
                                tcfg ['order_type'] = order_type
                                tcfg ['fee'] = fee
                                
                                log.debug ("tcfg: %s dcfg: %s" % (tcfg, dcfg))
                                return tcfg, dcfg
                            
    log.error ("unable to get config for %s: %s"%(exch_name, prod_name))
    return None, None    
    
    
def load_config (cfg_file):
    global WolfinchConfig
    global gDecisionConfig, gTradingConfig
    WolfinchConfig = readConf(cfg_file)
    
    log.debug ("cfg: %s" % WolfinchConfig)
    # sanitize the config
    for k, v in WolfinchConfig.items():
        if k == 'exchanges':
            if v == None:
                print ("Atleast one exchange need to be configured")
                return False
            prim = False
            for exch in v:
                for ex_k, ex_v in exch.items():
                    log.debug ("processing exch: %s val:%s" % (ex_k, ex_v))
                    #setup backfill config per exch, from global
                    if WolfinchConfig.get('backfill') :
                        log.info ("reading backfill global config")
                        ex_v['backfill'] = WolfinchConfig['backfill']
                    #setup candle_interval config per exch, from global
                    if WolfinchConfig.get('candle_interval') :
                        log.info ("reading candle_interval global config")
                        ex_v['candle_interval'] = WolfinchConfig['candle_interval']                        
                    products = ex_v.get('products')
                    if products != None and len(products):
                        log.debug ("processing exch products")
                        for prod in products:
                            for prod_name, _ in prod.items():
                                log.debug ("processing product %s:" % (prod_name))
#                                 tcfg, dcfg = get_product_config(prod_val)
                    role = ex_v.get('role')
                    if role == 'primary':
                        if prim == True:
                            print ("more than one primary exchange not supported")
                            return False
                        else:
                            prim = True
            if prim == False:
                print ("No primary exchange configured!!")
                return False
        elif k == 'stop_loss':
            for ex_k, ex_v in v.items():
                if ex_k == 'enabled':
                    gTradingConfig ['stop_loss_enabled'] = ex_v
                elif ex_k == 'kind':
                    gTradingConfig ['stop_loss_kind'] = ex_v
                    if ex_v not in ['simple', 'strategy']:        
                        gTradingConfig ['stop_loss_smart_rate'] = True
                elif ex_k == 'rate':
                    gTradingConfig ['stop_loss_rate'] = ex_v                 
        elif k == 'take_profit':
            for ex_k, ex_v in v.items():
                if ex_k == 'enabled':
                    gTradingConfig ['take_profit_enabled'] = ex_v
                elif ex_k == 'rate':
                    gTradingConfig ['take_profit_rate'] = ex_v                                    
        elif k == 'decision':
            for ex_k, ex_v in v.items():
                if ex_k == 'model':
                    gDecisionConfig ['model_type'] = ex_v
                elif ex_k == 'config':
                    gDecisionConfig ['model_config'] = ex_v     
        elif k == 'simulator':
            for ex_k, ex_v in v.items():
                if ex_k == 'enabled':
                    if ex_v == True:
                        log.debug ("simulator enabled")
                        sims.simulator_on = True
                    else:
                        log.debug ("simulator disabled")
                        sims.simulator_on = False
                elif ex_k == 'backtesting':
                    if ex_v == True:
                        log.debug ("backtesting enabled")
                        sims.backtesting_on = True
                    else:
                        log.debug ("backtesting disabled")       
                        sims.backtesting_on = False

        elif k == 'genetic_optimizer':
            for ex_k, ex_v in v.items():
                if ex_k == 'enabled':
                    if ex_v == True:
                        log.debug ("genetic_optimizer on")
                        sims.genetic_optimizer_on = True
                    else:
                        log.debug ("genetic_optimizer_on disabled")
                        sims.genetic_optimizer_on = False                     
                elif ex_k == 'N_POP':
                    sims.ga_config["GA_NPOP"] = ex_v
                elif ex_k == 'N_GEN':
                    sims.ga_config["GA_NGEN"] = ex_v
                elif ex_k == 'N_MP':
                    sims.ga_config["GA_NMP"] = ex_v
                elif ex_k == 'strategy':
                    sims.ga_config["strategy"] = ex_v
        elif k == 'ui':
            for ex_k, ex_v in v.items():
                if ex_k == 'enabled':
                    if ex_v == True:
                        log.debug ("ui enabled")
                        ui.integrated_ui = True
                    else:
                        log.debug ("ui disabled")
                        ui.integrated_ui = False
                if ex_k == 'port':
                    ui.port = ex_v                           
                
    if gTradingConfig ['stop_loss_enabled'] == False:
        gTradingConfig ['stop_loss_smart_rate'] = False
                        
#     print ("v: %s"%str(tradingConfig))
#     exit(1)
    log.debug ("config loaded successfully!")
    return True
    
def get_config ():
    return WolfinchConfig

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("cfgmgr - load")
#EOF
