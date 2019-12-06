#! /usr/bin/env python
# '''
#  Wolfinch Auto trading Bot
#  Desc:  exchange interactions Simulation
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

# from multiprocessing import Manager, Process

import strategy
from utils import getLogger

__name__ = "EA-EVAL"
log = getLogger (__name__)
log.setLevel(log.DEBUG)


g_eval_hook = None
g_strategy_name, g_strategy_class = None, None

def get_strategy_vars ():
    return g_strategy_class.config
    
def config_ga_strategy(strat_name):
    global g_strategy_name, g_strategy_class
    g_strategy_name = strat_name #ga_cfg['model_config']['strategy']
    log.info ("configuring GA for strategy - %s"%(g_strategy_name))
    g_strategy_class = strategy.get_strategy_by_name(g_strategy_name)
    
    if g_strategy_class == None:
        s = "Unable to configure strategy (%s)"%(g_strategy_name)
        log.critical (s)
        raise Exception(s)
    
def register_eval_hook (eval_hook):
    global g_eval_hook
    
    g_eval_hook = eval_hook

def eval_hook_call (config_kw):
    decision_cfg = {}
    decision_cfg['model_config'] = {"strategy": g_strategy_name, "params": config_kw["strategy_cfg"]}
    decision_cfg['model_type'] = "simple"
    
    stats = g_eval_hook (decision_cfg, config_kw["trading_cfg"])
    return stats
    
def eval_strategy_with_config (config_kw):
     
    log.debug ("config: %s"%(str(config_kw)))
    stats = eval_hook_call (config_kw)
     
    log.debug ("stats: %s"%str(stats))
     
    cur_profit = 0
    for _, k_v in stats.iteritems():
        cur_profit += round(k_v['fund']['current_realized_profit'], 2)
     
    return cur_profit

# def eval_strategy_with_config (config_kw):
#     ## TEST ### 
#     return 1000
#EOF    
