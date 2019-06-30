# '''
#  OldMonk Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''

# import requests
# import json
import uuid
import time
from datetime import datetime
# from dateutil.tz import tzlocal
from decimal import Decimal
import copy
import sys

from utils import getLogger
from market import feed_deQ, feed_Q_process_msg, get_market_list, flush_all_stats, get_all_market_stats, \
                             market_init, market_setup, Order
import db
import exchanges
import sim_exchange
from genetic import ga_main

#from market.order import Order, TradeRequest
#from market import feed_enQ

__name__ = "SIM-OPS"
log = getLogger (__name__)
log.setLevel (log.CRITICAL)

###### SIMULATOR Global switch ######
backtesting_on = False
import_only = False

####### Private #########
        
def finish_backtesting(market):
    log.info ("finish backtesting. market:%s"%(market.name))

    # sell acquired assets and come back to initial state
    market.close_all_positions()
    return True
    
def do_backtesting ():
    # don't sleep for backtesting    
    sleep_time = 0
    done = False
    all_done = 0
        
    for market in get_market_list():
        log.info ("backtest setup for market: %s num_candles:%d"%(market.name, market.num_candles))
        market.backtesting_idx = 0
                          
    while (all_done < 5) : 
        # check for the msg in the feed Q and process, with timeout
        done = True
        msg = feed_deQ(sleep_time)
        while (msg != None):
            feed_Q_process_msg (msg)
            msg = feed_deQ(0)        
        for market in get_market_list():
            market.update_market_states()
            # Trade only on primary markets
            if (market.primary == True and (market.backtesting_idx < market.num_candles - 1)):
#                 log.info ("BACKTEST(%d): processing on market: exchange (%s) product: %s"%(
#                     market.backtesting_idx, market.exchange_name, market.name))     
                signal = market.generate_trade_signal (market.backtesting_idx)
                market.consume_trade_signal (signal)
                if (sim_exchange.simulator_on):
                    sim_exchange.market_simulator_run (market)
                #if atleast one market is not done, we will continue
                done = False
                market.backtesting_idx += 1
            elif done == True:
                finish_backtesting(market)
                market.backtesting_idx = market.num_candles - 1
                if (sim_exchange.simulator_on):
                    sim_exchange.market_simulator_run (market)                
                #let's do few iterations and make sure everything is really done!
                all_done += 1 
                       
    #end While(true)
def show_stats ():
    flush_all_stats()

def sim_ga_init (decisionConfig, tradingConfig=None):
    global gConfig, gTradingConfig
    
    # TODO: FIXME: NOTE: add GA for trading config too
    if tradingConfig == None:
        tradingConfig = gTradingConfig
        
    #init 
    #1. Retrieve states back from Db
    db.init_order_db(Order)
    
    #2. Init Exchanges
    exchanges.init_exchanges(gConfig)
    
    #3. Init markets
    market_init (exchanges.exchange_list, decisionConfig, tradingConfig)
    
    #4. Setup markets
    market_setup()
    #init done    
    
    
############# Public APIs ######################
        
def market_backtesting_run ():
    """
    market backtesting 
    """
    log.debug("starting backtesting")    
    do_backtesting()
    log.info ("backtesting complete. ")
    show_stats ()
    
genetic_optimizer_on = False
ga_restart = False
gaDecisionConfig = {}
gConfig = None
ga_config = {"GA_NPOP":0, "GA_NGEN": 0, "GA_NMP": 0}
def market_backtesting_ga_hook (decisionConfig, tradingConfig=None):
    """
    market backtesting hook for ga
    """
    global backtesting_on
    
    sim_exchange.simulator_on = True
    backtesting_on = True
    
    sim_ga_init (decisionConfig, tradingConfig)
    
    log.debug("starting backtesting")    
    do_backtesting()
    log.info ("backtesting complete. ")
    
    
    stats = get_all_market_stats ()
    log.info ("Finalizing OldMonk")
    exchanges.close_exchanges ()
    
    return stats
    
def ga_sim_main (gCfg, decisionConfig, tradingConfig):    
    global gConfig, gaDecisionConfig, gTradingConfig, ga_restart
    
    gConfig, gaDecisionConfig, gTradingConfig = gCfg, decisionConfig, tradingConfig
    
    try:
        # start the GA algorithm here:
        ga_main (ga_config, gaDecisionConfig, ga_restart, evalfn = market_backtesting_ga_hook)
    except:
        print ("Unexpected error", sys.exc_info())
        raise        


#EOF