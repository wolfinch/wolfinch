#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: Main File implements Bot
# Copyright 2019, Joshith Rayaroth Koderi. All Rights Reserved.
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

from __future__ import print_function
from readconf import readConf
from logger import getLogger
import sims, ui

log = getLogger ('confmgr')
log.setLevel(log.INFO)
# Global Config 
WolfinchConfig = None
gDecisionConfig = {}
gTradingConfig = {"stop_loss_enabled": False,
                  "stop_loss_smart_rate": False,
                  "stop_loss_rate": 0,
                  "take_profit_enabled": False,
                  "take_profit_rate": 0}

def parse_product_config (cfg):
    global gDecisionConfig, gTradingConfig    
    parsed_tcfg = {}
    parsed_dcfg = {}    
    for k, v in cfg.iteritems():
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
        
        if k == 'stop_loss':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    parsed_tcfg ['stop_loss_enabled'] = ex_v
                elif ex_k == 'smart':
                    parsed_tcfg ['stop_loss_smart_rate'] = ex_v
                elif ex_k == 'rate':
                    parsed_tcfg ['stop_loss_rate'] = ex_v                    
        elif k == 'take_profit':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    parsed_tcfg ['take_profit_enabled'] = ex_v
                elif ex_k == 'rate':
                    parsed_tcfg ['take_profit_rate'] = ex_v                                    
        elif k == 'decision':
            for ex_k, ex_v in v.iteritems():
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
    return parsed_tcfg, parsed_dcfg


def get_product_config (exch_name, prod_name):
    global WolfinchConfig
    
    log.debug ("get_config for exch: %s prod: %s" % (exch_name, prod_name))
        
    # sanitize the config
    for k, v in WolfinchConfig.iteritems():
        if k == 'exchanges':
            if v == None:
                log.critical ("Atleast one exchange need to be configured")
                raise Exception("exchanges not configured")
            for exch in v:
                for ex_k, ex_v in exch.iteritems():
                    if ex_k.lower() != exch_name.lower():
                        continue
                    log.debug ("processing exch: %s val:%s" % (ex_k, ex_v))
                    products = ex_v.get('products')
                    if products != None and len(products):
                        log.debug ("processing exch products")
                        for prod in products:
                            for p_name, p_cfg in prod.iteritems():
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
    for k, v in WolfinchConfig.iteritems():
        if k == 'exchanges':
            if v == None:
                print ("Atleast one exchange need to be configured")
                return False
            prim = False
            for exch in v:
                for ex_k, ex_v in exch.iteritems():
                    log.debug ("processing exch: %s val:%s" % (ex_k, ex_v))
                    #setup backfill config per exch, from global
                    if WolfinchConfig.get('backfill') :
                        log.info ("reading backfill global config")
                        ex_v['backfill'] = WolfinchConfig['backfill']
                    products = ex_v.get('products')
                    if products != None and len(products):
                        log.debug ("processing exch products")
                        for prod in products:
                            for prod_name, _ in prod.iteritems():
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
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    gTradingConfig ['stop_loss_enabled'] = ex_v
                elif ex_k == 'smart':
                    gTradingConfig ['stop_loss_smart_rate'] = ex_v
                elif ex_k == 'rate':
                    gTradingConfig ['stop_loss_rate'] = ex_v                    
        elif k == 'take_profit':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    gTradingConfig ['take_profit_enabled'] = ex_v
                elif ex_k == 'rate':
                    gTradingConfig ['take_profit_rate'] = ex_v                                    
        elif k == 'decision':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'model':
                    gDecisionConfig ['model_type'] = ex_v
                elif ex_k == 'config':
                    gDecisionConfig ['model_config'] = ex_v     
        elif k == 'simulator':
            for ex_k, ex_v in v.iteritems():
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
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    if ex_v == True:
                        log.debug ("genetic_optimizer on")
                        sims.genetic_optimizer_on = True
                    else:
                        log.debug ("genetic_optimizer_on disabled")
                        sims.genetic_optimizer_on = False
#                 elif ex_k == 'config':
#                     sims.gaDecisionConfig ['model_config'] = {"strategy": ex_v["strategy"]} 
#                     sims.gaDecisionConfig ['model_type'] = 'simple'
#                     for t_k, t_v in ex_v.get("trading", {}).iteritems():
#                         if t_k == 'currency':
#                             sims.gaTradingConfig ['currency'] = t_v
#                         if t_k == 'fund_max_liquidity':
#                             sims.gaTradingConfig ['fund_max_liquidity'] = t_v
#                         if t_k == 'fund_max_per_buy_value':
#                             sims.gaTradingConfig ['fund_max_per_buy_value'] = t_v
#                         if t_k == 'asset_max_per_trade_size':
#                             sims.gaTradingConfig ['asset_max_per_trade_size'] = t_v
#                         if t_k == 'asset_min_per_trade_size':
#                             sims.gaTradingConfig ['asset_min_per_trade_size'] = t_v                        
#                         if t_k == 'stop_loss':
#                             for ex_tk, ex_tv in t_v.iteritems():
#                                 if ex_tk == 'enabled':
#                                     sims.gaTradingConfig ['stop_loss_enabled'] = ex_tv
#                                 elif ex_tk == 'smart':
#                                     sims.gaTradingConfig ['stop_loss_smart_rate'] = ex_tv
#                                 elif ex_tk == 'rate':
#                                     sims.gaTradingConfig ['stop_loss_rate'] = ex_v                    
#                         elif t_k == 'take_profit':
#                             for ex_tk, ex_tv in t_v.iteritems():
#                                 if ex_tk == 'enabled':
#                                     sims.gaTradingConfig ['take_profit_enabled'] = ex_tv
#                                 elif ex_tk == 'rate':
#                                     sims.gaTradingConfig ['take_profit_rate'] = ex_tv                       
                elif ex_k == 'N_POP':
                    sims.ga_config["GA_NPOP"] = ex_v
                elif ex_k == 'N_GEN':
                    sims.ga_config["GA_NGEN"] = ex_v
                elif ex_k == 'N_MP':
                    sims.ga_config["GA_NMP"] = ex_v
                elif ex_k == 'strategy':
                    sims.ga_config["strategy"] = ex_v
        elif k == 'ui':
            for ex_k, ex_v in v.iteritems():
                if ex_k == 'enabled':
                    if ex_v == True:
                        log.debug ("ui enabled")
                        ui.integrated_ui = True
                    else:
                        log.debug ("ui disabled")
                        ui.integrated_ui = False
                if ex_k == 'port':
                    ui.port = ex_v                           
                
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
