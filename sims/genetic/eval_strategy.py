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

from multiprocessing import Manager, Process

from strategy import EMA_DEV
from utils import getLogger

__name__ = "EA-EVAL"
log = getLogger (__name__)

g_mp_manager = None
g_eval_hook = None

def get_strategy ():
    return EMA_DEV
    
def register_eval_hook (eval_hook):
    global g_eval_hook, g_mp_manager
    
    g_eval_hook = eval_hook
    
    g_mp_manager = Manager()

def eval_hook_remote (in_dict, out_dict):
    
    stats = g_eval_hook (in_dict)
    
    out_dict['return_vars'] = stats
    
def eval_hook_mp_call (config_kw):
    
    ret_dict = g_mp_manager.dict()
    
    decision_cfg = {}
    decision_cfg['model_config'] = {"strategy": "EMA_DEV", "params": config_kw}
    decision_cfg['model_type'] = "simple"

    p = Process(target=eval_hook_remote, args=(decision_cfg, ret_dict))
    
    p.start()
    p.join()
    
    return ret_dict['return_vars']

def eval_hook_call (config_kw):
    decision_cfg = {}
    decision_cfg['model_config'] = {"strategy": "EMA_DEV", "params": config_kw}
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

#EOF    