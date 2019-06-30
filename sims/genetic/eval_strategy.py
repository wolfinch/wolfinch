#! /usr/bin/env python
# '''
#  OldMonk Auto trading Bot
#  Desc:  exchange interactions Simulation
# Copyright 2019, Joshith Rayaroth Koderi, OldMonk Bot. All Rights Reserved.
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

# from multiprocessing import Manager, Process

import strategy
from utils import getLogger

__name__ = "EA-EVAL"
log = getLogger (__name__)
log.setLevel(log.INFO)


g_mp_manager = None
g_eval_hook = None
g_strategy_name, g_strategy_class = None, None

def get_strategy_vars ():
    return g_strategy_class.config
    
def config_ga_strategy(ga_cfg):
    global g_strategy_name, g_strategy_class
    g_strategy_name = ga_cfg['model_config']['strategy']
    log.info ("configuring GA for strategy - %s"%(g_strategy_name))
    g_strategy_class = strategy.get_strategy_by_name(g_strategy_name)
    
    if g_strategy_class == None:
        s = "Unable to configure strategy (%s)"%(g_strategy_name)
        log.critical (s)
        raise Exception(s)
    
def register_eval_hook (eval_hook):
    global g_eval_hook, g_mp_manager
    
    g_eval_hook = eval_hook

def eval_hook_call (config_kw):
    decision_cfg = {}
    decision_cfg['model_config'] = {"strategy": g_strategy_name, "params": config_kw}
    decision_cfg['model_type'] = "simple"
    
    stats = g_eval_hook (decision_cfg)
    return stats
    
def eval_strategy_with_config (config_kw):
     
    log.debug ("config: %s"%(str(config_kw)))
    stats = eval_hook_call (config_kw)
     
    log.debug ("stats: %s"%str(stats))
     
    cur_profit = 0
    for _, k_v in stats.iteritems():
        cur_profit += k_v['fund']['current_realized_profit']
     
    return cur_profit

# def eval_strategy_with_config (config_kw):
#     ## TEST ### 
#     return 1000
#EOF    