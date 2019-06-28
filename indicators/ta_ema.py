# '''
#  Desc: Market Exponential Moving Average (EMA) implementation using ta-lib
#  (c) https://mrjbq7.github.io/ta-lib/
#  (c) OldMonk Bot
# '''

from decimal import Decimal
from indicator import Indicator
import numpy as np
import talib

# from utils import getLogger
# log = getLogger ('TA_EMA')
# log.setLevel(log.DEBUG)

class EMA (Indicator):
    '''
    Exponential moving Average (EMA) market indicator implementation using TA library
    '''
    
    def __init__(self, name, period=12):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return Decimal(0)
        
        val_array = np.array(map(lambda x: float(x['ohlc'].close), candles[-self.period:]))
        
        #calculate ema
        cur_ema = talib.EMA (val_array, timeperiod=self.period)
        
#         log.info ("TA_EMA: %g"%cur_ema)
        return Decimal(cur_ema[-1])
        