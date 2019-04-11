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

class Model ():
    def __init__(self, X_shape):
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
        
    def train(self, X_train, Y_train):
        self.regressor.fit(X_train, Y_train, epochs = 100, batch_size = 32)
        

    def test(self):
        dataset_total = pd.concat((dataset_train['Open'], dataset_test['Open']), axis = 0)
        inputs = dataset_total[len(dataset_total) - len(dataset_test) - 60:].values
        inputs = inputs.reshape(-1,1)
        inputs = sc.transform(inputs)
        X_test = []
        for i in range(60, 76):
            X_test.append(inputs[i-60:i, 0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
        predicted_stock_price = regressor.predict(X_test)
        predicted_stock_price = sc.inverse_transform(predicted_stock_price)        
    
######### ******** MAIN ****** #########
if __name__ == '__main__':
    import market
    
    print ("Model engine init, importing historic data\n")
    
    prod = {"id" : "BTC-USD", "display_name" : "BTC-USD"}
    class gdax:
        __name__ = "gdax"
        
    m = market.Market(product=prod, exchange=gdax)
    m._import_historic_candles(local_only=True)
    m._calculate_historic_indicators()
    m._process_historic_strategies()
    
    print ("Model Engine Start\n")
    model = Model (10)
    
    print ("Model init complete, training starts.. \n")

    print ("All done, bye!")
#EOF