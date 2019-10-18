# '''
#  OldMonk Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''

# import requests
# import json
# import uuid
# import time
# from dateutil.tz import tzlocal
import sys

from utils import getLogger
from market import feed_deQ, feed_Q_process_msg, get_market_list, flush_all_stats, get_all_market_stats, \
                             market_init, market_setup
# import db
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
simulator_on = False
import_only = False

####### Private #########
        
def finish_backtesting(market):
    log.info ("finish backtesting. market:%s"%(market.name))

    # sell acquired assets and come back to initial state
    market.close_all_positions()
    return True
    
def do_backtesting (simulator_on=False):
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
            market.cur_candle_time = market.market_indicators_data[market.backtesting_idx]['ohlc'].time
            # Trade only on primary markets
            if (market.primary == True and (market.backtesting_idx < market.num_candles - 1)):
#                 log.info ("BACKTEST(%d): processing on market: exchange (%s) product: %s"%(
#                     market.backtesting_idx, market.exchange_name, market.name))     
                signal = market.generate_trade_signal (market.backtesting_idx)
                market.consume_trade_signal (signal)
                
                if (simulator_on):
                    sim_exchange.market_simulator_run (market)
                #if atleast one market is not done, we will continue
                done = False
                market.backtesting_idx += 1
            elif done == True:
                finish_backtesting(market)
                market.backtesting_idx = market.num_candles - 1
                if (simulator_on):
                    sim_exchange.market_simulator_run (market)                
                #let's do few iterations and make sure everything is really done!
                all_done += 1 
                       
    #end While(true)
def show_stats ():
    flush_all_stats()

def sim_ga_init (decisionConfig, tradingConfig=None):
    global gConfig, gaTradingConfig
    
    # TODO: FIXME: NOTE: add GA for trading config too
    if tradingConfig == None:
        tradingConfig = gaTradingConfig
         
    #init 
    #1. Retrieve states back from Db
#     db.init_order_db(Order)
    
    #2. Init Exchanges
    exchanges.init_exchanges(gConfig)
    
    # cfg hook, mock from Oldmonk.py
    def get_prod_cfg (exch_name, prod_name):
        return tradingConfig, decisionConfig
    
    #3. Init markets
    market_init (exchanges.exchange_list, get_prod_cfg)
    
    #4. Setup markets
    market_setup()
    #init done    
    
    
############# Public APIs ######################
        
def market_backtesting_run (sim_on=False):
    """
    market backtesting 
    """
    log.debug("starting backtesting")    
    do_backtesting(sim_on)
    log.info ("backtesting complete. ")
    show_stats ()
    
genetic_optimizer_on = False
ga_restart = False
gaDecisionConfig = {}
gaTradingConfig = {}
gConfig = None
ga_config = {"GA_NPOP":0, "GA_NGEN": 0, "GA_NMP": 0}
def market_backtesting_ga_hook (decisionConfig, tradingConfig=None):
    """
    market backtesting hook for ga
    """
    global backtesting_on, simulator_on
    
    simulator_on = True
    backtesting_on = True
    
    sim_ga_init (decisionConfig, tradingConfig)
    
    log.debug("starting backtesting")    
    do_backtesting(simulator_on)
    log.info ("backtesting complete. ")
    
    
    stats = get_all_market_stats ()
    log.info ("Finalizing OldMonk")
    exchanges.close_exchanges ()
    
    return stats
    
def ga_sim_main (gCfg, decisionConfig, tradingConfig):    
    global gConfig, gaDecisionConfig, gaTradingConfig, ga_restart
    
    gConfig, gaDecisionConfig, gaTradingConfig = gCfg, decisionConfig, tradingConfig
    
    try:
        # start the GA algorithm here:
        ga_main (ga_config, gaDecisionConfig, tradingConfig, ga_restart, evalfn = market_backtesting_ga_hook)
    except:
        print ("Unexpected error", sys.exc_info())
        raise        


#EOF