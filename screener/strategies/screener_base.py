#
# Wolfinch Auto trading Bot
# Desc:  Market Screener Abstract Class Implementation
#  Copyright: (c) 2017-2021 Joshith Rayaroth Koderi
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
        
class Screener (metaclass=ABCMeta):
    @abstractmethod
    def __init__ (self, name="", interval=300):
        ''' 
        Init for the screener class
        '''
        self.name = name
        self.interval = interval
        self.updated = False
        self.update_time = 0
        self.ticker_stats = {}
        self.ticker_filtered = []
    def __str__ (self):
        return "{Message: TODO: FIXME: implement}"
    def configure (self):
        pass
    @abstractmethod
    def update(self):
        pass
    @abstractmethod    
    def screen(self):
        pass
    def get_screened(self):
        return []    

#EOF