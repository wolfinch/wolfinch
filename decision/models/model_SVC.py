#! /usr/bin/env python
# Wolfinch Auto trading Bot
# Desc: SVM (support Vector Machines) Model
# 
#  Copyright: (c) 2017-2019 Joshith Rayaroth Koderi
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

from sklearn import svm
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
        
        self.lab_enc = preprocessing.LabelEncoder()

        # Init Keras
        self.classifier = svm.SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
                            decision_function_shape='ovo', degree=3, gamma='scale', kernel='rbf',
                            max_iter=-1, probability=False, random_state=None, shrinking=True,
                            tol=0.001, verbose=False)

        
    def scaleX(self, X):
        log.debug("X.Shape: %s"%str(X.shape))
        for i in range(len(self.scX)):
            log.debug ("X%d shape; %s: %s"%(i, str(X[:,:,i].shape), X[:,:,i]))
            X[:,:,i] = self.scX[i].fit_transform(X[:,:,i])
        return X
    def scaleY(self, Y):
        return self.scY.fit_transform(Y)
            
    def train(self, X_train, Y_train):
        
        X = np.array(X_train).reshape(X_train.shape[0], X_train.shape[1]*X_train.shape[2])
        Y_encoded = self.lab_enc.fit_transform(Y_train)
        
        self.classifier.fit(X, Y_encoded)
        

    def predict(self, X_pred):        
        X = np.array(X_pred).reshape(X_pred.shape[0], X_pred.shape[1]*X_pred.shape[2])

        Y_label = self.classifier.predict(X)
        Y_pred = self.lab_enc.inverse_transform(Y_label)
        return self.scY.inverse_transform(Y_pred.reshape(-1, 1))   
    
    def summary(self):
        pass
            
    
#EOF
