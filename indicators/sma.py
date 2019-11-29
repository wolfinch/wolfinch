# '''
#  Desc: Market Simple Moving Average (SMA) implementation 
#  (c) Wolfinch Bot
# '''

from indicator import Indicator

class SMA (Indicator):
    '''
    Simple moving Average (SMA) market indicator implementation
    '''
    
    def __init__(self, name, period=15):
        self.name = name
        self.period = period
                
    def calculate(self, candles):
        if len(candles) < self.period:
            return 0
#        print ("len sma: "+str(len(data)))
        #(time, o, h,l,c, vol)
        return  float(sum( map (lambda x: x['ohlc'].close, candles[-self.period:])))/self.period
        
