'''
 Wolfinch Auto trading Bot
 Desc: Exchanges impl Abstract Class Implementation
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
'''
from abc import ABCMeta, abstractmethod

class Exchange(metaclass=ABCMeta):
    @abstractmethod
    def __init__ (self):
        ''' 
        Init for the exchange class
        '''
        pass
    
    def __str__ (self):
        return "{Message: Exchange Abstract Class}"

    def market_init (self):
        pass
    def close (self):
        pass    
    
    def add_candle(self, market):
        pass
    
    @abstractmethod
    def buy (self):
        pass
    @abstractmethod
    def sell (self):
        pass
    @abstractmethod
    def get_order (self):
        pass
    @abstractmethod
    def cancel_order (self):
        pass
    @abstractmethod
    def add_products (self):
        pass
    @abstractmethod
    def delete_products (self):
        pass    
    @abstractmethod
    def get_products (self):
        pass
    @abstractmethod
    def get_accounts (self):
        pass     
    @abstractmethod
    def get_historic_rates (self):
        pass        
    @abstractmethod
    def get_product_order_book (self):
        pass
    
#EOF    
