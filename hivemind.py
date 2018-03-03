#!/usr/bin/env python

#hivemind.py
#
#by Joe Hahn
#jmh.datasciences@gmail.com
#3 March 2018
#
#these helper functions are called bu hivemind.ipynb

#imports
import numpy as np
import pandas as pd

#generate game data
def play_hivemind(N_buckets, N_turns):
    bucket_yield_mean = np.arange(N_buckets)/10.0 
    bucket_yield_sigma = 2*bucket_yield_mean
    bucket_yields_list = []
    best_bucket_list = []
    for idx in range(N_turns):
        bucket_yields = np.random.normal(loc=bucket_yield_mean, scale=bucket_yield_sigma)
        bucket_yields_list += [bucket_yields]
        best_bucket = np.zeros(N_buckets)
        best_idx = bucket_yields.argmax()
        best_bucket[best_idx] = 1.0
        best_bucket_list += [best_bucket]
    bucket_yields = np.array(bucket_yields_list)
    best_bucket = np.array(best_bucket_list)
    return bucket_yields, best_bucket, bucket_yield_mean, bucket_yield_sigma

#this helper function builds a simple MLP classifier
def mlp_classifier(N_inputs, N_middle_layer, N_outputs, dropout_fraction):
    from keras.models import Sequential
    from keras.layers import Dense, Dropout
    model = Sequential()
    model.add(Dense(N_inputs, activation='elu', input_shape=(N_inputs,)))
    model.add(Dropout(dropout_fraction))
    model.add(Dense(N_middle_layer, activation='elu'))
    model.add(Dropout(dropout_fraction))
    model.add(Dense(N_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

#
def compute_net_yields(bucket_yields, best_bucket_probability):
    #generate dataframe of yields, probabilities, and net 
    N_buckets = bucket_yields.shape[1]
    cols = ['yield' + str(idx) for idx in range(N_buckets)]
    net_yields = pd.DataFrame(bucket_yields, columns=cols)
    net_yields['net'] = 0.0
    #best_bucket_probability = model.predict(bucket_yields)
    for idx in range(N_buckets):
        prob_col = 'prob' + str(idx)
        net_yields[prob_col] = best_bucket_probability[:, idx]
        yield_col = 'yield' + str(idx)
        net_yields['net'] += net_yields[yield_col]*net_yields[prob_col]
    cols = [col for col in net_yields.columns if (col != 'net')] + ['net']
    net_yields = net_yields[cols]
    return net_yields
