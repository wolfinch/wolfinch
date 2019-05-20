'''
 OldMonk Auto trading Bot
 Desc: Exchanges list 
         Configure the required exchanges here. 
 (c) OldMonk Bot
'''
from exchanges.cbpro import CBPRO
from exchanges.binanceClient import Binance

exchanges = [
        Binance,
        CBPRO
    ]


                    
#EOF    