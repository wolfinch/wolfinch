# '''
#  Desc: Market Exponential Moving Average (EMA) implementation 
#  (c) OldMonk Bot
# '''

from decimal import Decimal
from indicator import Indicator

class DEFUNCT_EMA (Indicator):
    '''
    Exponential moving Average (EMA) market indicator implementation
    '''
    
    def __init__(self, name, period=12):
        self.name = name
        self.period = period
        self._multiplier = Decimal(2)/ (period +1)
                
    def calculate(self, candles):
        # The formula below is for a 10-day EMA:
        # 
        # SMA: 10 period sum / 10 
        # Multiplier: (2 / (Time periods + 1) ) = (2 / (10 + 1) ) = 0.1818 (18.18%)
        # EMA: {Close - EMA(previous day)} x multiplier + EMA(previous day). 
        
        candles_len = len(candles)
        if candles_len < self.period:
            return Decimal(0)
        
        prev_ema = candles[candles_len - 2][self.name]
        if prev_ema == 0:
            #SMA 
            prev_ema =  Decimal(sum( map (lambda x: x['ohlc'].close, candles)))/self.period
        
        #calculate ema
        return Decimal(((candles[candles_len - 1]['ohlc'].close - prev_ema )*self._multiplier + prev_ema))
        