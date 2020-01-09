#
# Wolfinch Auto trading Bot
# Desc:  Market Strategy Abstract Class Implementation
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

from abc import ABCMeta, abstractmethod

class Strategy(metaclass=ABCMeta):
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

    def indicator (self, candles, name, period=0, history=-1):
        if period == 0:
            i_name = name
        else:
            i_name = '%s%s'%(name, str(period))
        if history == -1:
            return candles[-1][i_name]
        else:
            return [c[i_name] for c in candles[-history:]]
            
    def crossover (self, x, y):
        pass
        
    def slope (self, x, y):
        pass
    
    @abstractmethod
    def generate_signal (self):
        '''
        Trade Signale in range(-3..0..3), ==> (strong sell .. 0 .. strong buy) 0 is neutral (hold) signal 
        '''
        return 0
        
    
