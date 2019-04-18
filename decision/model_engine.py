#! /usr/bin/env python
# OldMonk Auto trading Bot
# Desc: Model engine creates trading model crunching data
# 
# Copyright 2018, Joshith Rayaroth Koderi. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from sklearn.preprocessing import MinMaxScaler

class Model ():
    def __init__(self, X_shape):
        # init preprocessor/scaler
        self.scX = MinMaxScaler(feature_range = (0, 1))
        self.scY = MinMaxScaler(feature_range = (0, 1))
        
        # Init Keras
        self.regressor = Sequential()
        
        self.regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (X_shape, 1)))
        self.regressor.add(Dropout(0.2))
        
        self.regressor.add(LSTM(units = 50, return_sequences = True))
        self.regressor.add(Dropout(0.2))
        
        self.regressor.add(LSTM(units = 50, return_sequences = True))
        self.regressor.add(Dropout(0.2))
        
        self.regressor.add(LSTM(units = 50))
        self.regressor.add(Dropout(0.2))
        
        self.regressor.add(Dense(units = 1))
        
        self.regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
        
    def scaleX(self, X):
        return self.scX.fit_transform(X)
    def scaleY(self, Y):
        return self.scY.fit_transform(Y)
            
    def train(self, X_train, Y_train):
        self.regressor.fit(X_train, Y_train, epochs = 100, batch_size = 32)
        

    def test(self, X):        
        Y_pred = self.regressor.predict(X)
        
        return self.scY.inverse_transform(Y_pred.reshape(-1, 1))   
    
######### ******** MAIN ****** #########
if __name__ == '__main__':
    import market
#     from keras.utils import plot_model
    import  numpy as np
    import matplotlib.pyplot as plt
        
    def plot_res (Y_orig, Y_Pred):
        plt.plot(Y_orig, color = 'black', label = 'Real Y')
        plt.plot(Y_Pred, color = 'green', label = 'Pred Y')
        plt.title('Prediction')
        plt.xlabel('Time')
        plt.ylabel('Y Prediction')
        plt.legend()
        plt.show()
        
    def normalize_input(model, cdl_list):
        x_list = map (lambda x: x['ohlc'].close, cdl_list)
        
        x_train = []
        y_train = []
        for i in range (60, len(x_list)):
            x_train.append(x_list[i-60:i])
            if i < len(x_list)-1:
                if x_list[i] < x_list[i+1]:
                    y_train.append(5)
                elif x_list[i] > x_list[i+1]:
                    y_train.append(-5)
                else:
                    y_train.append(0)
            else:
                y_train.append(0)
        
        x_arr, y_arr = np.array(x_train), np.array(y_train).reshape(-1, 1)
        print ("x_arr shape: %s y_arr shape: %s"%(x_arr.shape, y_arr.shape))
        
        # tranform
        x, y = model.scaleX(x_arr), model.scaleY(y_arr)
        
        #reshape, 
        X_train, Y_train = np.reshape(x, (x.shape[0], x.shape[1], 1)), y
        print ("X_train shape: %s Y_train shape: %s"%(X_train.shape, Y_train.shape))
        
        
        return X_train, Y_train
    
#         predicted_stock_price = regressor.predict(X_test)
#         predicted_stock_price = sc.inverse_transform(predicted_stock_price)        
    
    print ("Model engine init, importing historic data\n")
    
    print ("Model Engine Start\n")
    model = Model (60)
#     plot_model(model.regressor, to_file='model.png')
#     exit()
    
    prod = {"id" : "BTC-USD", "display_name" : "BTC-USD"}
    class gdax:
        __name__ = "gdax"
        
    m = market.Market(product=prod, exchange=gdax)
    m._import_historic_candles(local_only=True)
    m._calculate_historic_indicators()
    m._process_historic_strategies()
    
    print ("Model init complete, training starts.. \n")
    X_train, Y_train = normalize_input(model, m.get_indicator_list())
    
    model.train(X_train, Y_train)
    print ("Training done")
    
    print ("Testing .. ")
    Y_pred = model.test(X_train)
    print ("Testing done..\n ploting..")
    
    plot_res(Y_train, Y_pred)

    print ("All done, bye!")
#EOF