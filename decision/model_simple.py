#! /usr/bin/env python
# OldMonk Auto trading Bot
# Desc: Simple DeNoising Auto Encoder (DAE) Model
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

from utils import getLogger

log = getLogger ('decision_simple')
log.setLevel(log.DEBUG)

class Model ():
    EPOCH = 300
    BATCH_SIZE = 64
    def __init__(self, X_shape, load_path=""):
        # init preprocessor/scaler as the number of feature layers and o/p layer
#         X_shape = X_shape_in[0] * X_shape_in[1]
#         log.debug ("X_Shape: %s norm_shape: %d"%(str(X_shape_in), X_shape))
        log.debug ("X_Shape: %s "%(str(X_shape)))

        
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
        
    def save(self, path):
        self.regressor.save(path)
        
    def load (self, path):
        self.
    
#EOF