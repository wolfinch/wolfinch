#! /usr/bin/env python
'''
 Desc: 
 Global Market Indicators Configuration. 
 ref. implementation.
 All the globally available market Indicators are instantiated and configured here.
 If a market specific Indicators list is required, a similar config may be made specific to the market
 (c) Joshith Rayaroth Koderi
'''

from indicators.sma import SMA
from indicators.ema import EMA
from indicators.ta_ema import TA_EMA
from indicators.bollinger import BBANDS


market_indicators = []
init_done = False

def Configure ():
    global init_done, market_indicators
    #### Configure the Strategies below ######
    
    if init_done:
        return market_indicators
    
    # SMA15, SMA50
    sma15 = SMA ('sma15', 15)
    sma50 = SMA ('sma50', 50)
    
    #EMA12, EMA26
    ema12 = EMA ('ema12', 12)
    ema26 = EMA ('ema26', 26)
        
    #TA_EMA12, TA_EMA26
    ta_ema12 = TA_EMA ('ta_ema12', 12)
    ta_ema26 = TA_EMA ('ta_ema26', 26)
            
    bbands = BBANDS ('bbands') # default timeperiod 20
            
    # List of all the available strategies
    global market_indicators
    market_indicators = [
            sma15,
            sma50,
            ema12,
            ema26,
            ta_ema12,
            ta_ema26,
            bbands
        ]
    
    #### Configure the Strategies - end ######
    init_done = True
    return market_indicators

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Indicators Test")
    Configure ()
    
    
#EOF