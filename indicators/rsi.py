# '''
#  Desc: Relative Strength Index (Momentum Indicators) implementation using ta-lib
#  (c) https://mrjbq7.github.io/ta-lib/
#  (c) OldMonk Bot
# '''

from decimal import Decimal
from indicator import Indicator
import numpy as np
import talib

class RSI (Indicator):
    '''
    Relative Strength Index (Momentum Indicators) market indicator implementation using TA library
    '''
    
    def __init__(self, name, period=14):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period+1:
            return Decimal(0)
        
        val_array = np.array(map(lambda x: float(x['ohlc'].close), candles[-(self.period+1):]))
        
        #calculate 
        cur_rsi = talib.RSI (val_array, timeperiod=self.period)
        
        return Decimal(cur_rsi[-1])
        