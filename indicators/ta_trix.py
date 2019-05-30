# '''
#  Desc: TRIX - 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA implementation using ta-lib
#  (c) https://mrjbq7.github.io/ta-lib/
#  (c) OldMonk Bot
# '''

from decimal import Decimal
from indicator import Indicator
import numpy as np
import talib

# from utils import getLogger
# log = getLogger ('TA_TRIX')
# log.setLevel(log.DEBUG)

class TA_TRIX (Indicator):
    '''
    TRIX - 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA market indicator implementation using TA library
    '''
    
    def __init__(self, name, period=90):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return Decimal(0)
        
        val_array = np.array(map(lambda x: float(x['ohlc'].close), candles[-self.period:]))
        
        #calculate trix
        cur_trix = talib.TRIX (val_array, timeperiod=self.period/3)
        
#         log.critical ("TA_TRIX: %s"%str(cur_trix[-1]))
        return Decimal(cur_trix[-1])
        