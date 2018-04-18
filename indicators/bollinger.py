# '''
#  Desc: Bollinger Bands (Overlap Studies) implementation using ta-lib
#  (c) https://mrjbq7.github.io/ta-lib/
#  (c) Joshith Rayaroth Koderi
# '''

from decimal import Decimal
from indicator import Indicator
import numpy as np
import talib

class BBANDS (Indicator):
    '''
    Bollinger Bands (Overlap Studies) market indicator implementation using TA library
    '''
    
    def __init__(self, name, period=20):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return Decimal(0)
        
        val_array = np.array(map(lambda x: float(x['ohlc'].close), candles[-self.period:]))
        
        #calculate 
        (upperband, middleband, lowerband) = talib.BBANDS (val_array, timeperiod=self.period)
        
        return (upperband[-1], middleband[-1], lowerband[-1])
        