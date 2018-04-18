# '''
#  Desc: Moving Average Convergence/Divergence (Momentum Indicators) implementation using ta-lib
#  (c) https://mrjbq7.github.io/ta-lib/
#  (c) Joshith Rayaroth Koderi
# '''

from indicator import Indicator
import numpy as np
import talib

class MACD (Indicator):
    '''
    Moving Average Convergence/Divergence (Momentum Indicators) implementation using TA library
    default:         fastperiod: 12
        slowperiod: 26
        signalperiod: 9
        period = slowperiod + signal - 1
    '''
    
    def __init__(self, name, period=34):
        self.name = name
        self.period = period
                
    def calculate(self, candles):        
        candles_len = len(candles)
        if candles_len < self.period:
            return (0, 0, 0)
        
        close_array = np.array(map(lambda x: float(x['ohlc'].close), candles[-self.period:]))
        
        #calculate 
        (macd, macdsignal, macdhist) = talib.MACD (close_array)
        
        return (macd[-1], macdsignal[-1], macdhist[-1])
        