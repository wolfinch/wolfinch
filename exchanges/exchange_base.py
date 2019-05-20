'''
 OldMonk Auto trading Bot
 Desc: Exchanges impl Abstract Class Implementation
 (c) OldMonk Bot
'''
from abc import ABCMeta, abstractmethod

class Exchange:
    __metaclass__ = ABCMeta

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