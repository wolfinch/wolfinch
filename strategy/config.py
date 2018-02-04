#! /usr/bin/env python
'''
 Desc: 
 Global Market Strategy Configuration. 
 ref. implementation.
 All the globally available market strategies are instantiated and configured here.
 If a market specific strategy list is required, a similar config may be made specific to the market
 (c) Joshith Rayaroth Koderi
'''

market_strategies = []
def Configure ():
    global market_strategies
    #### Configure the Strategies below ######
    market_strategies = []
    
    #### Configure the Strategies - end ######

######### ******** MAIN ****** #########
if __name__ == '__main__':
    print ("Market Strategy Test")
    Configure()
    
#EOF