'''
 Desc: Market Simple Moving Average (SMA) implementation 
 (c) Joshith Rayaroth Koderi
'''

from indicators.indicator import Indicator

class SMA (Indicator):
    '''
    Simple moving Average (SMA) market indicator implementation
    '''
    
    def __init__(self, name, period=15):
        self.name = name
        self.period = period
                
    def calculate(self):
        pass
