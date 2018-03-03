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
    bucket_yield_mean = np.linspace(0.0, 0.005, num=N_buckets)
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

#compute per-turn bucket yields, and compounded net yield
def compute_net_gains(bucket_yields, model):
    #generate dataframe of yields, probabilities, and net 
    N_buckets = bucket_yields.shape[1]
    cols = ['gain' + str(idx) for idx in range(N_buckets)]
    net_gains = pd.DataFrame(bucket_yields, columns=cols)
    net_gains['net_gain'] = 1.0
    best_bucket_probability = model.predict(bucket_yields)
    for idx in range(N_buckets):
        prob_col = 'prob' + str(idx)
        net_gains[prob_col] = best_bucket_probability[:, idx]
        gain_col = 'gain' + str(idx)
        net_gains['net_gain'] += net_gains[gain_col]*net_gains[prob_col]
    net_gains['compound_gain'] = net_gains['net_gain'].copy()
    for idx in range(len(net_gains)):
        if (idx > 0):
            net_gains.loc[idx, 'compound_gain'] = \
                net_gains.loc[idx, 'net_gain']*net_gains.loc[idx-1, 'compound_gain']
    net_gains['turn'] = net_gains.index
    cols = net_gains.columns.tolist()
    cols.remove('turn')
    cols.remove('net_gain')
    cols.remove('compound_gain')
    cols = ['turn'] + cols + ['net_gain', 'compound_gain']
    net_gains = net_gains[cols]
    return net_gains, best_bucket_probability
