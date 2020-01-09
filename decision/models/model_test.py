#! /usr/bin/env python
# Wolfinch Auto trading Bot
# Desc: Model engine creates trading model crunching data
# 
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


import  numpy as np
import matplotlib.pyplot as plt

from .model_simple_DAE import Model
# from model_LSTM import Model
# from model_SVC import Model

from utils import getLogger
import market

log = getLogger ('MODEL-TEST')
log.setLevel(log.CRITICAL)
    
X_RANGE = 60

        
def plot_res (X_train, Y_orig, Y_Pred):
#         plt.plot(X_train, color = 'blue', label = 'Real X')    
    new_arr = np.zeros([(Y_orig.shape[0] - Y_Pred.shape[0]), 1])
#     log.debug ("y_shape: %s c_shape: %s"%(new_arr.shape, Y_Pred.shape))
    new_arr = np.append(new_arr, Y_Pred, 0)
    plt.plot(Y_orig, color = 'black', label = 'Real Y')
    plt.plot(new_arr, color = 'green', label = 'Pred Y')
    plt.title('Prediction')
    plt.xlabel('Time')
    plt.ylabel('Y Prediction')
    plt.legend()
    plt.show()
        
def create_x_list(indi_list, strat_list):
    def form_x_from_ind (ind, strat):
        x = [ind['ohlc'].time, ind['ohlc'].close, ind['ohlc'].open , ind['ohlc'].high, ind['ohlc'].low, ind['ohlc'].volume]
        for v in strat.values():
            x.append(v)
#         list(map(lambda s: x.append(s), iter(strat.values())))
#             x += [yy]
#             print ("x: %s"%x)
#             print ("ind %s"%ind['ohlc'].close)
#             print ("strat %s"%strat)
        return x
    x_list =  list(map (form_x_from_ind, indi_list, strat_list))
#         print ("x_list: %s"%x_list)
    return x_list
        
def create_y_list(x_list):
    y_train = []
     
    for i in range (0, len(x_list)):
        log.debug("x: %s"%x_list[i])
        d = 0
        p = x_list[i][1]
        for s in x_list[i: (i+5 if i+5 < len(x_list) else len(x_list))]:
            if s[1] < p:
                d -= 1
            elif s[1] > p:
                d += 1
                p = s[1]
        y_train.append(d)
    return y_train        

#     def create_y_list(x_list):
#         y_train = []
#         
#         for i in range (X_RANGE, len(x_list)-2):
#             y_train.append(x_list[i+1])
#         y_train.append(x_list[-2])
#         return y_train  
        
def normalize_input(model, x_list, y_list_in):
    x_train = []
        
        
    for i in range (X_RANGE, len(x_list)):
        x_train.append(x_list[i-X_RANGE:i])
            
    y_list = y_list_in[X_RANGE:]
        
    x_arr, y_arr = np.array(x_train), np.array(y_list).reshape(-1, 1)
    print ("x_arr shape: %s y_arr shape: %s"%(x_arr.shape, y_arr.shape))
        
    # tranform
    x, y = model.scaleX(x_arr), model.scaleY(y_arr)
#         print ("X_train: \n%s"%x)
    print ("Y_train: \n%s"%y_list)
    #reshape
    X_train, Y_train = np.reshape(x, (x.shape[0], x.shape[1], -1)), y
#     print ("X_train shape: %s Y_train shape: %s"%(X_train.shape, Y_train.shape))
    return x, y_arr, X_train, Y_train
    
#         predicted_stock_price = regressor.predict(X_test)
#         predicted_stock_price = sc.inverse_transform(predicted_stock_price)        
#     def create_x_list(indi_list):
#         def form_x_from_ind (ind):
#             x = []
#             print ("indicator matrix ",ind)
#             for k,v in ind.iteritems():
#                 if k == 'ohlc':
#                     x += [v.open, v.high, v.low, v.close, v.volume]
#                 elif k == 'MACD':
#                     pass
#                 else:
#                     x += [v]
#             return x
#         return map (form_x_from_ind, indi_list)

        
#     plot_model(model.regressor, to_file='model.png')
#     exit()
def merge_x_list(x1_list, x2_list):
    x_list = []
    i =0; j = 0
    found = False
    for _ in range(min(len(x1_list), len(x2_list))):
        if x1_list[i][0] == x2_list[j][0]:
            found = True
            break
        elif x1_list[i][0] > x2_list[j][0]:
            j += 1
        else:
            i += 1
    if found == False:
        print ("unable to find commond timeline")
        return []
    print ("found common base at i:%d j: %d time: %d"%(i, j, x1_list[i][0]))
    xi = i
        
    for _ in range(min(len(x1_list), len(x2_list))):
        if x1_list[i][0] != x2_list[j][0]:
            print ("found mismatch base at i:%d j: %d time: %d, stop merge"%(i, j, x1_list[i][0]))                
            break
                
#             x_list[k] = map (lambda x1, x2: x1[1:]+x2[1:], x1_list[i], x2_list[j])
        x_list.append ( x1_list[i][1:] + x2_list[j][1:])
            
        i += 1
        j += 1
    return x_list, xi
    

######### ******** MAIN ****** #########
if __name__ == '__main__':

    prod = {"id" : "BTC-USD", "display_name" : "BTC-USD"}
    
    #CBPRO
    class gdax:
        name = "CBPRO"
        
    m_cb = market.Market(product=prod, exchange=gdax)
    m_cb._import_historic_candles(local_only=True)
    m_cb._calculate_historic_indicators()
    m_cb._process_historic_strategies()
    
    print ("Model init complete, training starts.. \n")
    indicator_list = m_cb.get_indicator_list()
    strategies_list = m_cb.get_strategies_list()
    x_cb_list = create_x_list(indicator_list, strategies_list)
    
    y_cb_list = create_y_list(x_cb_list)
    
    #Binance
    class bnc:
        name = "binance"
        
    m_bnc = market.Market(product=prod, exchange=bnc)
    m_bnc._import_historic_candles(local_only=True)
    m_bnc._calculate_historic_indicators()
    m_bnc._process_historic_strategies()
    
    print ("Model init complete, training starts.. \n")
    indicator_list = m_bnc.get_indicator_list()
    strategies_list = m_bnc.get_strategies_list()
    x_bnc_list = create_x_list(indicator_list, strategies_list)
    
    y_bnc_list = create_y_list(x_bnc_list)
    
    x_list, x_start = merge_x_list (x_cb_list, x_bnc_list)
    y_list = y_cb_list[x_start: len(x_list)]
    
    if (x_list == None or len(x_list) == 0):
        print ("Unable to get x_list")
        exit(1)
    else:
        print ("x_list: len(%d) "%(len(x_list)))
#         print ("x_list: %s len(%d) "%(x_list, len(x_list)))    

    # TEST MODEL
    print ("len x y",len(x_list[0]),len(y_list))
    for x, y in zip (x_list, y_list):
        x.append(y)
#     list(map (lambda x,y : x.append(y), x_list, y_list))
    # TEST MODEL
    
    
    x_arr = np.array(x_list).reshape(len(x_list), -1)
    print ("Model engine init, importing historic data\n")
    
    print ("Model Engine Start.. X.shape:%s\n"%(str(x_arr.shape)))
    model = Model ((X_RANGE, x_arr.shape[1]))

    X, Y, X_train, Y_train = normalize_input(model, x_list, y_list)
    
    model.train(X_train[:-60, :, :], Y_train[:-60, :])
    print ("Training done")
    
    print ("Testing .. ")
    Y_pred = model.predict(X_train[-60:,:,:])
    print ("Testing done.. summary:\n \n ploting..")
    model.summary()
    
    plot_res(x_arr, Y, Y_pred)

    print ("All done, bye!")
#EOF
