#
# OldMonk Auto trading Bot
# Desc:  Market Strategy Abstract Class Implementation
# Copyright 2018, OldMonk Bot. All Rights Reserved.
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

from abc import ABCMeta, abstractmethod

class Strategy:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__ (self):
        ''' 
        Init for the strategy class
        '''
        pass
#         self._indicator_list = {}
    
    def __str__ (self):
        return "{Message: TODO: FIXME: jork: implement}"

    def configure (self):
        pass
    
    def set_indicator (self, name, periods=[]):
        
        if not hasattr(self, "_indicator_list"):
            self._indicator_list = {}
        ind = self._indicator_list.get(name, None)
        if ind:
            ind.update(periods)
        else:
            self._indicator_list[name] = set(periods)
            
    def get_indicators (self):
        if not hasattr(self, "_indicator_list"):
            return {}
        else:        
            return self._indicator_list

    def get_indicator_current (self, candles, name, period=0):
        if period == 0:
            return candles[-1][name]
        else:    
            return candles[-1]['%s%d'%(name, period)]
        
    @abstractmethod
    def generate_signal (self):
        '''
        Trade Signale in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        return 0
        
    