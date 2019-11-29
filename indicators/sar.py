# '''
#  Desc: Parabolic SAR (Overlap Studies) implementation using ta-lib
#  (c) https://mrjbq7.github.io/ta-lib/
#  (c) Wolfinch Bot
# '''

from indicator import Indicator
import numpy as np
import talib

class SAR (Indicator):
    '''
    Parabolic SAR (Overlap Studies) implementation using TA library
    '''
    
    def __init__(self, name, period=20):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return 0
        
        high_array = np.array(map(lambda x: float(x['ohlc'].high), candles[-self.period:]))
        low_array = np.array(map(lambda x: float(x['ohlc'].low), candles[-self.period:]))
        
        #calculate 
        sar = talib.SAR (high_array, low_array)
        
        return sar[-1]
        
