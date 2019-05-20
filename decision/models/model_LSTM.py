#! /usr/bin/env python
# OldMonk Auto trading Bot
# Desc: LSTM (Long Short-Term memory) Model
# 
# Copyright 2018, OldMonk Bot. All Rights Reserved.
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
from utils import getLogger

log = getLogger ('MODEL')
log.setLevel(log.DEBUG)

class Model ():
    EPOCH = 300
    BATCH_SIZE = 64
    def __init__(self, X_shape):
        # init preprocessor/scaler as the number of feature layers and o/p layer
        self.scX = []
        for _ in range (X_shape[1]):
            self.scX += [MinMaxScaler(feature_range = (0, 1))]
        self.scY = MinMaxScaler(feature_range = (0, 1))
        
        # Init Keras
        self.regressor = Sequential()
        
        self.regressor.add(LSTM(units = 50, return_sequences = True, input_shape = X_shape))
        self.regressor.add(Dropout(0.2))
        
        self.regressor.add(LSTM(units = 50, return_sequences = True))
        self.regressor.add(Dropout(0.2))
        
        self.regressor.add(LSTM(units = 50, return_sequences = True))
        self.regressor.add(Dropout(0.2))
        
        self.regressor.add(LSTM(units = 50))
        self.regressor.add(Dropout(0.2))
        
        self.regressor.add(Dense(units = 1))
#         self.regressor.add(Dense(units = 1, activation="tanh"))
#         self.regressor.add(Dense(units = 1, activation="softmax"))
        

        self.regressor.compile(optimizer = 'adam', loss = 'mean_squared_error', metrics=['accuracy'])
#         self.regressor.compile(optimizer = 'rmsprop', loss = 'mean_squared_error', metrics=['accuracy'])
#         self.regressor.compile(optimizer='rmsprop', loss='mean_squared_error', metrics=['accuracy'])

        
    def scaleX(self, X):
        log.debug("X.Shape: %s"%str(X.shape))
        for i in range(len(self.scX)):
            log.debug ("X%d shape; %s: %s"%(i, str(X[:,:,i].shape), X[:,:,i]))
            X[:,:,i] = self.scX[i].fit_transform(X[:,:,i])
        return X
    def scaleY(self, Y):
        return self.scY.fit_transform(Y)
            
    def train(self, X_train, Y_train):
        self.regressor.fit(X_train, Y_train, epochs = self.EPOCH, batch_size = self.BATCH_SIZE)
        

    def predict(self, X):        
#         Y_pred = self.regressor.predict_classes(X)
        Y_pred = self.regressor.predict(X)
        return self.scY.inverse_transform(Y_pred.reshape(-1, 1))   
    
    def summary(self):
        self.regressor.summary()    
    
#EOF