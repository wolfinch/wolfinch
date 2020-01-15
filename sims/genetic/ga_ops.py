#! /usr/bin/env python
# '''
#  Wolfinch Auto trading Bot
#  Desc:  Genetic Optimizer
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



import random

from . import eval_strategy
from utils import getLogger

# __name__ = "EA-OPS"
log = getLogger (__name__)
log.setLevel (log.CRITICAL)


#TODO: FIXME: lot of hacky code here to fix deap ind generator issue with strat dict


def selectOneMax(individual, res_dict):
    log.debug (" individual: %s"%(individual))
    
    fitnessVal = eval_strategy.eval_strategy_with_config(individual)
    
    log.debug ("fitnessVal: %d"%fitnessVal)
    
    res_dict["res"] = fitnessVal,
#     return fitnessVal,


def createOffSpringStrategy(indA, indB):
    ind1, ind2 = indA,indB
    
    size = len(ind1)
    cxpoint1 = random.randint(1, size)

    keys = random.sample(list(ind1), cxpoint1)
    
    log.debug ("size: %d cxpoint1: %d keys; %s"%(size, cxpoint1, keys))
    
    for key in keys:
        #swap values
        log.debug ("swapping key: %s"%(key))
        tmp = ind1[key]
        ind1[key], ind2[key] = ind2[key], tmp
            
    indA= ind1
    indB= ind2
    return indA, indB

def createOffSpringTradecfg(indA, indB):
    ind1, ind2 = indA,indB
    
    size = len(ind1)
    cxpoint1 = random.randint(1, size)

    keys = random.sample(list(ind1), cxpoint1)
    
    log.debug ("size: %d cxpoint1: %d keys; %s"%(size, cxpoint1, keys))
    
    for key in keys:
        #swap values
        log.debug ("swapping key: %s"%(key))
        tmp = ind1[key]
        ind1[key], ind2[key] = ind2[key], tmp
            
    indA= ind1
    indB= ind2
    return police_tradingcfg_gen(indA), police_tradingcfg_gen(indB)

def createOffSpring(indA, indB):

    indA["strategy_cfg"], indB["strategy_cfg"] = createOffSpringStrategy(indA["strategy_cfg"], indB["strategy_cfg"])
    indA["trading_cfg"], indB["trading_cfg"] = createOffSpringTradecfg(indA["trading_cfg"], indB["trading_cfg"])

    return indA, indB
    
def createMutantStrategy(indS, indpb):
    
    conf = eval_strategy.get_strategy_vars()
    log.debug ("original: %s"%(indS))
    for key in indS.keys():
        rand = random.random()
        if rand < indpb:
            indS [key] = genParamVal(conf, key)
#             raise Exception("rand: %f %s"%(rand, ind))
    individual = indS
    log.debug ("mutant: %s"%(indS))    
    return individual

def createMutantTradecfg(indT, indpb):
    conf = TradingConfig
        
    log.debug ("original: %s"%(indT))
    for key in indT.keys():
        rand = random.random()
        if rand < indpb:
            indT [key] = genParamVal(conf, key)
#             raise Exception("rand: %f %s"%(rand, ind))

    indT = police_tradingcfg_gen (indT)

    individual = indT
    log.debug ("mutant: %s"%(indT))
    return individual

def createMutant (individual, indpb):
    individual["strategy_cfg"] = createMutantStrategy(individual["strategy_cfg"], indpb)
    individual["trading_cfg"] = createMutantTradecfg(individual["trading_cfg"], indpb)
    return individual,

def configGenerator ():
    return {"strategy_cfg": strategyGenerator(), "trading_cfg": tradingcfgGenerator()}

TradingConfig = {
        'stop_loss_enabled' : {'default': True, 'var': {'type': bool}},
        'stop_loss_smart_rate' : {'default': False, 'var': {'type': bool}},        
        'stop_loss_rate' : {'default': 5, 'var': {'type': int, 'min': 1, 'max': 10, 'step': 1 }},        
        'stop_loss_kind' : {'default': 'simple', 'var': {'type': str, 'choices': ['simple', 'strategy', 'trailing', 'ATR']}},
        'stop_loss_atr_period' : {'default': 50, 'var': {'type': int, 'min': 10, 'max': 200, 'step': 10 }},          
        'take_profit_enabled' : {'default': True, 'var': {'type': bool}},
        'take_profit_kind' : {'default': 'simple', 'var': {'type': str, 'choices': ['simple', 'strategy']}},        
        'take_profit_rate' : {'default': 10, 'var': {'type': int, 'min': 2, 'max': 20, 'step': 1 }}
        }
GaTradingConfig = {}

def police_tradingcfg_gen (t_cfg):
    for param_key, param_val in GaTradingConfig.items():
        t_cfg [param_key] = param_val
    
    if (t_cfg["stop_loss_enabled"] == False):
        t_cfg["stop_loss_smart_rate"] = False
        t_cfg["stop_loss_rate"] = 0
        t_cfg["stop_loss_kind"] = "simple"
    elif t_cfg["stop_loss_rate"] == 0 :
        if ('ATR' in t_cfg["stop_loss_kind"] ):
            t_cfg["stop_loss_enabled"] = True
            t_cfg["stop_loss_smart_rate"] = True
        elif 'strategy' == t_cfg["stop_loss_kind"]:
            t_cfg["stop_loss_enabled"] = True
            t_cfg["stop_loss_smart_rate"] = False
        else:
            t_cfg["stop_loss_enabled"] = False
            t_cfg["stop_loss_smart_rate"] = False            
            t_cfg["stop_loss_kind"] = "simple"
    if 'ATR' == t_cfg["stop_loss_kind"]:
        #just mutated, need to find ATR rate too. 
        if not t_cfg.get("stop_loss_atr_period"):
            t_cfg["stop_loss_atr_period"] = genParamVal(TradingConfig, "stop_loss_atr_period")
        t_cfg["stop_loss_kind"] = "ATR%d"%t_cfg["stop_loss_atr_period"]
        t_cfg["stop_loss_rate"] = 0
    if 'strategy' == t_cfg["stop_loss_kind"]:
        t_cfg["stop_loss_rate"] = 0
                
    if (t_cfg["take_profit_enabled"] == False):
        t_cfg["take_profit_rate"] = 0
        t_cfg["take_profit_kind"] = "simple"
    elif t_cfg["take_profit_kind"] == "strategy":
        t_cfg["take_profit_rate"] = 0                  
    elif t_cfg["take_profit_rate"] == 0:
        t_cfg["take_profit_enabled"] = False
    
    if t_cfg.get("stop_loss_atr_period"):
        del(t_cfg["stop_loss_atr_period"])    
    return t_cfg
    
def tradingcfgGenerator ():
    cfg_gen = {}
    
    for param_key in TradingConfig.keys():
        cfg_gen [param_key] = genParamVal(TradingConfig, param_key)
        
    cfg_gen = police_tradingcfg_gen(cfg_gen)
                
    log.critical ("strat: %s"%(cfg_gen))

    return cfg_gen

def strategyGenerator ():
    #strat_confg = { 'period' : {'default': 50, 'var': {'type': int, 'min': 20, 'max': 100, 'step': 1 }},}
    
    # TODO: TBD: NOTE: enhance initial pop generation logic. Right now pure random, We can use heuristics for better pop
    
    conf = eval_strategy.get_strategy_vars()
    strat_gen = {}
    
    for param_key in conf.keys():
        strat_gen [param_key] = genParamVal(conf, param_key)
#         yield param_key, val    
#         yield val
    log.debug ("strat: %s"%(strat_gen))
    return strat_gen

def genParamVal (conf, param_key):
        
    param_conf = conf[param_key]
    var = param_conf['var']
    tp = var['type']
    
    val = 0
    if tp == int:
        r_min = var['min']
        r_max = var['max']
        r_step = var.get('step')
        #get val
        val = random.randrange (r_min, r_max+1, r_step)
    elif tp == float :
        r_min = var['min']
        r_max = var['max']
        r_step = var.get('step')
        val = round(random.uniform (r_min, r_max), 2)
    elif tp == bool:
        val = random.choice([False, True])
    elif tp == str:
        choices = var['choices']
        val = random.choice(choices)
    else:
        raise Exception( "Unsupported var type (%s)"%(repr(tp))) 
    
    return val

if __name__ == "__main__":
    import strategy.strategies.ema_rsi as ema_rsi
    
    eval_strategy.g_strategy_class = ema_rsi.EMA_RSI
    
    print ("conf: %s"%(eval_strategy.get_strategy_vars()))
    
    indA = configGenerator ()
    indB = configGenerator ()
    
    print ("\n\nindA: %s \n\n indB:%s "%(indA, indB))
    offA, offB = createOffSpring (indA, indB)
    
    res_dict = dict()
    m = selectOneMax (indA, res_dict)
    print ("indA: %s \n indB: %s \n offA: %s \n offB: %s val: %s"%(indA, indB, offA, offB, m))
    
#EOF
