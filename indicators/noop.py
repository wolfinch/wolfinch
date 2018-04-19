# '''
#  Desc: NO-OP Indicator implementation
#    Returns the closing price on each candle
#  (c) Joshith Rayaroth Koderi
# '''

from decimal import Decimal
from indicator import Indicator
import numpy as np
import talib

class NOOP (Indicator):
    '''
     No-Op indicator 
    '''
    def __init__(self, name):
        self.name = name
        self.period = 1
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len == 0:
            return 0
        return Decimal(candles[-1]['ohlc'].close)
        