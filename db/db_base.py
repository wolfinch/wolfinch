'''
 OldMonk Auto trading Bot
 Desc: Db Abstract Class Implementation
 (c) OldMonk Bot
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
        return "{Message: Indicator Abstract Class}"
    
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
