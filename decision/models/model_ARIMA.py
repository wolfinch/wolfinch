#! /usr/bin/env python
# OldMonk Auto trading Bot
# Desc: ARIMA (autoRegressive Integrated Moving Avg) Model
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

from statsmodels.tsa.arima_model import ARIMA

from sklearn.preprocessing import MinMaxScaler
from utils import getLogger
import  numpy as np
from sklearn import preprocessing
from sklearn import utils

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

        
    def scaleX(self, X):
        log.debug("X.Shape: %s"%str(X.shape))
        for i in range(len(self.scX)):
            log.debug ("X%d shape; %s: %s"%(i, str(X[:,:,i].shape), X[:,:,i]))
            X[:,:,i] = self.scX[i].fit_transform(X[:,:,i])
        return X
    def scaleY(self, Y):
        return self.scY.fit_transform(Y)
            
    def train(self, X_train, Y_train):
        
        self.model.fit(X, Y_encoded)
        

    def predict(self, X_pred):        
        X = np.array(X_pred).reshape(X_pred.shape[0], X_pred.shape[1]*X_pred.shape[2])

        Y_label = self.model.predict(X)
        Y_pred = self.lab_enc.inverse_transform(Y_label)
        return self.scY.inverse_transform(Y_pred.reshape(-1, 1))
    
    def summary(self):
        self.model.summary()
    
#EOF