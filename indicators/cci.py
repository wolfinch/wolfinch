# '''
#  Desc: Commodity Channel Index (Momentum Indicators) implementation using ta-lib
#  (c) https://mrjbq7.github.io/ta-lib/
#  (c) OldMonk Bot
# '''

from indicator import Indicator
import numpy as np
import talib

class CCI (Indicator):
    '''
    Commodity Channel Index (Momentum Indicators) implementation using TA library
    '''
    
    def __init__(self, name, period=14):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return 0
        
        close_array = np.array(map(lambda x: float(x['ohlc'].close), candles[-self.period:]))
        high_array = np.array(map(lambda x: float(x['ohlc'].high), candles[-self.period:]))
        low_array = np.array(map(lambda x: float(x['ohlc'].low), candles[-self.period:]))
        
        #calculate 
        cci = talib.CCI (high_array, low_array, close_array, timeperiod=self.period)
        
        return cci[-1]
        