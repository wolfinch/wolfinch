'''
 wolfinch Auto trading Bot
 Desc: Db Abstract Class Implementation
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
'''

from abc import ABCMeta, abstractmethod

class DbBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__ (self):
        ''' 
        Init for the DB class
        '''
        pass
    
    def __str__ (self):
        return "{Message: Db Abstract Class}"
    
    @abstractmethod
    def clear_db (self):
        pass
    
    @abstractmethod    
    def clear_table (self, table):
        pass
        
    @abstractmethod    
    def insert_one (self, entry, table):
        pass
    
    @abstractmethod    
    def delete_one (self, entry, table):
        pass
    
    @abstractmethod    
    def insert_many (self, entries):
        pass
    
    @abstractmethod    
    def delete_many (self, entries):
        pass
    
#EOF
