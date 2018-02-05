'''
 Desc: Market Simple Moving Average (SMA) implementation 
 (c) Joshith Rayaroth Koderi
'''

from indicator import Indicator

class SMA (Indicator):
    '''
    Simple moving Average (SMA) market indicator implementation
    '''
    
    def __init__(self, name, period=15):
        self.name = name
        self.period = period
                
    def calculate(self, data):
        if len(data) < self.period:
            return 0
        #(time, o, h,l,c, vol)
        return  (reduce (lambda x,y: x+y, map (lambda x: x['ohlc'][4], data), 0))/self.period
        
