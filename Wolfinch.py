#! /usr/bin/env python3
'''
# Wolfinch Auto trading Bot
# Desc: Main File implements Bot
#  Copyright: (c) 2017-2020 Joshith Rayaroth Koderi
#  This file is part of Wolfinch.
# 
#  Wolfinch is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  Wolfinch is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with Wolfinch.  If not, see <https://www.gnu.org/licenses/>.
'''


import time
import sys
# import os
import traceback
import argparse
from decimal import getcontext
import random
import logging, matplotlib
from utils import getLogger, get_product_config, load_config, get_config
import sims
import exchanges
from market import market_init, market_setup, get_market_list, \
                 feed_Q_process_msg, feed_deQ, get_market_by_product
import db
import stats
import ui
from ui import ui_conn_pipe

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
log = getLogger('Wolfinch')
log.setLevel(log.INFO)

gRestart = False

# global Variables
MAIN_TICK_DELAY = 0.500  # 500 milli


def Wolfinch_init():

    # seed random
    random.seed()

    # 1. Retrieve states back from Db
#     db.init_order_db(Order)

    # setup ui if required
    if ui.integrated_ui:
        ui.ui_conn_pipe = ui.ui_mp_init(ui.port)
        if ui.ui_conn_pipe is None:
            log.critical("unable to setup ui!! ")
            print("unable to setup UI!!")
            sys.exit(1)

    # 2. Init Exchanges
    exchanges.init_exchanges(get_config())

    # 3. Init markets
    market_init(exchanges.exchange_list, get_product_config)

    # 4. Setup markets
    market_setup(restart=gRestart)

    # 5. start stats thread
    stats.start()


def Wolfinch_end():
    log.info("Finalizing Wolfinch")
    exchanges.close_exchanges()

    # stop stats thread
    log.info("waiting to stop stats thread")
    stats.stop()

    ui.ui_mp_end()
    log.info("all cleanup done.")


def wolfinch_main():
    """
    Main Function for Wolfinch
    """
    feed_deQ_fn = feed_deQ
    feed_Q_process_msg_fn = feed_Q_process_msg

    integrated_ui = ui.integrated_ui
    ui_conn_pipe = ui.ui_conn_pipe

    sleep_time = MAIN_TICK_DELAY
    while True:
        cur_time = time.time()
#         log.critical("Current(%d)Sleep time left:%s"%(cur_time, str(sleep_time)))
        # check for the msg in the feed Q and process, with timeout
        msg = feed_deQ_fn(sleep_time)
#         log.critical("Current(%d)"%(time.time()))
        while msg is not None:
            feed_Q_process_msg_fn(msg)
            msg = feed_deQ_fn(0)
        if integrated_ui == True:
            process_ui_msgs(ui_conn_pipe)
        for market in get_market_list():
            process_market(market)
        # '''Make sure each iteration take exactly LOOP_DELAY time'''
        sleep_time = (MAIN_TICK_DELAY -(time.time()- cur_time))
#         if sleep_time < 0 :
#             log.critical("******* TIMING SKEWED(%f)******"%(sleep_time))
        sleep_time = 0 if sleep_time < 0 else sleep_time
    # end While(true)


def process_market(market):
#     """
#     processing routine for one exchange
#     """
    log.debug("processing Market: exchange(%s)product: %s" %(market.exchange_name, market.name))
    # update various market states on tick
    market.update_market_states()

    # Trade only on primary markets
    if market.new_candle is True:
        if market.primary is True:
            signal, sl, tp = market.generate_trade_signal()
            market.consume_trade_signal(signal, sl, tp)
            if sims.simulator_on:
                sims.market_simulator_run(market, sims.backtesting_on)
        stats.stats_update_order_bulk(market)

    # check pending trades periodically and takes actions(this logic is rate-limited)
    market.watch_pending_orders()

    # commit market states to the db periodically(this logic is rate-limited)
    market.lazy_commit_market_states()


def process_ui_trade_notif(msg):
    exch = msg.get("exchange")
    product = msg.get("product")
    side = msg.get("side")
    signal = msg.get("signal")
    m = get_market_by_product(exch, product)
    if not m:
        log.error("Unknown exchange/product exch: %s prod: %s" %(exch, product))
    else:
        log.info("Manual Trade Req: exch: %s prod: %s side: %s signal: %s" %(
            exch, product, side, str(signal)))
        m.consume_trade_signal(signal)

def process_ui_pause_trading_notif(msg):
    exch = msg.get("exchange")
    product = msg.get("product")
    buy_pause = msg.get("buy_pause")
    sell_pause = msg.get("sell_pause")

    m = get_market_by_product(exch, product)
    if not m:
        log.error("Unknown exchange/product exch: %s prod: %s" %(exch, product))
    else:
        log.info("pause trading on exch: %s prod: %s" %(exch, product))
        m.pause_trading(buy_pause, sell_pause)

def process_ui_get_markets_rr(msg, ui_conn_pipe):
    log.debug("enter")
    m_dict = {}
    for m in get_market_list():
        p_list = m_dict.get(m.exchange_name)
        if not p_list:
            m_dict[m.exchange_name] = [{"product_id": m.product_id,
                                        "buy_paused": m.trading_paused_buy,
                                        "sell_paused": m.trading_paused_sell}]
        else:
            p_list.append({"product_id": m.product_id,
                           "buy_paused": m.trading_paused_buy,
                           "sell_paused": m.trading_paused_sell})

    msg["type"] = "GET_MARKETS_RESP"
    msg["data"] = m_dict
    ui_conn_pipe.send(msg)

def process_ui_get_market_indicators_rr(msg, ui_conn_pipe):
    log.debug("enter")
    exch = msg.get("exchange")
    product = msg.get("product")
    num_periods = msg.get("periods", 0)
    start_time = msg.get("start_time", 0)
    market = get_market_by_product(exch, product)
    ind_list = {}
    if market:
        ind_list = market.get_indicator_list(num_periods, start_time)
    msg["type"] = "GET_MARKET_INDICATORS_RESP"
    msg["data"] = ind_list
    ui_conn_pipe.send(msg)
    
def process_ui_get_positions_rr(msg, ui_conn_pipe):
    log.debug("enter")
    exch = msg.get("exchange")
    product = msg.get("product")
    start_time = msg.get("start_time", 0)
    end_time = msg.get("end_time", 0)
    market = get_market_by_product(exch, product)
    pos_list = {}
    if market:
        log.info ("get positions ")
        pos_list = market.get_positions_list(start_time, end_time)
    msg["type"] = "GET_MARKET_POSITIONS_RESP"
    msg["data"] = pos_list
    ui_conn_pipe.send(msg)    
    
def process_ui_msgs(ui_conn_pipe):
    try:
        while ui_conn_pipe.poll():
            msg = ui_conn_pipe.recv()
            err = msg.get("error", None)
            if  err is not None:
                log.error("error in the pipe, ui finished: msg:%s" %(err))
                raise Exception("UI error - %s" %(err))
            else:
                log.info ("ui_msg: %s"%(msg))
                msg_type = msg.get("type")
                if msg_type == "TRADE":
                    process_ui_trade_notif(msg)
                elif msg_type == "GET_MARKETS":
                    process_ui_get_markets_rr(msg, ui_conn_pipe)
                elif msg_type == "GET_MARKET_INDICATORS":
                    process_ui_get_market_indicators_rr(msg, ui_conn_pipe)                    
                elif msg_type == "GET_MARKET_POSITIONS":
                    process_ui_get_positions_rr(msg, ui_conn_pipe)                        
                elif msg_type == "PAUSE_TRADING":
                    process_ui_pause_trading_notif(msg)
                else:
                    log.error("Unknown ui msg type: %s", msg_type)
    except Exception as e:
        log.critical("exception %s on ui" %(str(e)))
        raise e


def clean_states():
    ''' 
    clean states
    '''
    log.info("Clearing Db")
    db.clear_db()
    stats.clear_stats()

def arg_parse():
    '''
    arg parse
    '''
    global gRestart
    parser = argparse.ArgumentParser(description='Wolfinch Auto Trading Bot')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0.1')
    parser.add_argument("--clean",
                        help='Clean states,dbs and exit. Clear all the existing states',
                        action='store_true')
    parser.add_argument("--config", help='Wolfinch Global config file')
    parser.add_argument("--backtesting", help='do backtesting', action='store_true')
    parser.add_argument("--import_only", help='do import only and exit ', action='store_true')
    parser.add_argument("--restart", help='restart from the previous state', action='store_true')
    parser.add_argument("--ga_restart", help='restart genetic analysis from previous state',
                        action='store_true')

    args = parser.parse_args()

    if args.clean:
        clean_states()
        exit(0)

    if args.config:
        log.debug("config file: %s" % (str(args.config)))
        if False == load_config(args.config):
            log.critical("Config parse error!!")
            parser.print_help()
            exit(1)
        else:
            log.debug("config loaded successfully!")
#             exit(0)
    else:
        parser.print_help()
        exit(1)

    if args.import_only:
        log.debug("import_only enabled")
        sims.import_only = True
        sims.genetic_optimizer_on = False
        sims.backtesting_on = False
    else:
        log.debug("import_only disabled")
        sims.import_only = False

    if args.restart:
        log.debug("restart enabled")
        print("Restarting from previous state")
        gRestart = True
    else:
        log.debug("restart disabled")
        gRestart = False

    if args.ga_restart:
        log.debug("ga_restart enabled")
        sims.ga_restart = True
    else:
        log.debug("import_only disabled")
        sims.ga_restart = False

    if args.backtesting:
        log.debug("backtesting enabled")
        sims.backtesting_on = True
        # sims.simulator_on = True
#     else:
#         log.debug("backtesting disabled")
#         sims.backtesting_on = False

#     log.debug("sims.backtesting_on: %d"%(sims.backtesting_on))
#     exit(1)


######### ******** MAIN ****** #########
if __name__ == '__main__':
    '''
    main entry point
    '''

    arg_parse()

    getcontext().prec = 8  # decimal precision

    print("Starting Wolfinch Trading Bot..")

    try:
        if sims.genetic_optimizer_on:
            print("starting genetic backtesting optimizer")
            sims.ga_sim_main(get_config(), get_product_config)
            print("finished running genetic backtesting optimizer")
            sys.exit()
        Wolfinch_init()
        if sims.import_only:
            log.info("import only")
            raise SystemExit

        if sims.backtesting_on:
            sims.market_backtesting_run(sims.simulator_on)
            if ui.integrated_ui:
                wolfinch_main()
            else:
                raise SystemExit
        else:
            #slow down a little bit. wait to get to a whole minute boundary, we might get some initial trades wrong here. that's ok
            # this initial delay will help us to get cleaner candles when we are operational
            log.debug("waiting to start wolfinch main")
            time.sleep(60 - time.time()%60)
            log.info("Starting Main forever loop")
            wolfinch_main()
    except(KeyboardInterrupt, SystemExit):
        Wolfinch_end()
        sys.exit()
    except Exception as e:
        log.critical("Unexpected error: exception: %s" %(traceback.format_exc()))
        print("Unexpected error: exception: %s" %(traceback.format_exc()))
        Wolfinch_end()
        raise
#         traceback.print_exc()
#         os.abort()
    # '''Not supposed to reach here'''
    print("\nWolfinch end")

# EOF
