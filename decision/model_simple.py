#! /usr/bin/env python
# OldMonk Auto trading Bot
# Desc: Simple Model
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
from keras.layers import Dropout
from keras.layers import Flatten
import  numpy as np

from sklearn.preprocessing import MinMaxScaler
from utils import getLogger

log = getLogger ('MODEL')
log.setLevel(log.DEBUG)

class Model ():
    EPOCH = 300
    BATCH_SIZE = 64
    def __init__(self, X_shape):
        # init preprocessor/scaler as the number of feature layers and o/p layer
#         X_shape = X_shape_in[0] * X_shape_in[1]
#         log.debug ("X_Shape: %s norm_shape: %d"%(str(X_shape_in), X_shape))
        log.debug ("X_Shape: %s "%(str(X_shape)))
        
        self.scX = []
        for _ in range (X_shape[1]):
            self.scX += [MinMaxScaler(feature_range = (0, 1))]
        self.scY = MinMaxScaler(feature_range = (0, 1))
        
        # Init Keras
        self.regressor = Sequential()
        
        self.regressor.add(Dense(units = 100, init='uniform', activation='relu', input_shape = X_shape))
#         self.regressor.add(Dropout(0.2))
        
        self.regressor.add(Dense(units = 100, activation='relu'))
#         self.regressor.add(Dropout(0.2))
        
        self.regressor.add(Dense(units = 100, activation='relu'))
#         self.regressor.add(Dropout(0.2))
        
        self.regressor.add(Dense(units = 100, activation='relu'))
#         self.regressor.add(Dropout(0.2))
        
        self.regressor.add(Flatten())
        
        self.regressor.add(Dense(units = 1, activation='sigmoid'))
#         self.regressor.add(Dense(units = 1, activation="tanh"))
#         self.regressor.add(Dense(units = 1, activation="softmax"))
        

        self.regressor.compile(optimizer = 'adam', loss = 'mean_squared_error', metrics=['accuracy'])
#         self.regressor.compile(optimizer = 'rmsprop', loss = 'mean_squared_error', metrics=['accuracy'])
#         self.regressor.compile(optimizer='rmsprop', loss='mean_squared_error', metrics=['accuracy'])
        self.regressor.summary()

        
    def scaleX(self, X):
        log.debug("X.Shape: %s"%str(X.shape))
        for i in range(len(self.scX)):
            log.debug ("X%d shape; %s: %s"%(i, str(X[:,:,i].shape), X[:,:,i]))
            X[:,:,i] = self.scX[i].fit_transform(X[:,:,i])
        return X
    def scaleY(self, Y):
        return self.scY.fit_transform(Y)
            
    def train(self, X, Y_train):
#         X = np.array(X_train).reshape(X_train.shape[0], X_train.shape[1]*X_train.shape[2])
        
        self.regressor.fit(X, Y_train, epochs = self.EPOCH, batch_size = self.BATCH_SIZE)
        

    def predict(self, X_pred):        
#         X = np.array(X_pred).reshape(X_pred.shape[0], X_pred.shape[1]*X_pred.shape[2])
        Y_pred = self.regressor.predict(X_pred)
        return self.scY.inverse_transform(Y_pred.reshape(-1, 1))   
    
    def summary(self):
        self.regressor.summary()    
    
#EOF