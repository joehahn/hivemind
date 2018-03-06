#!/usr/bin/env python

#hivemind.py
#
#by Joe Hahn
#jmh.datasciences@gmail.com
#3 March 2018
#
#these helper functions are called by hivemind.ipynb

#imports
import numpy as np
import pandas as pd

#generate game data
def make_bucket_yields(N_buckets, N_turns, SNR, lag):
    bucket_yield_mean = np.linspace(0.0, 0.005, num=N_buckets)
    bucket_yield_sigma = (1.0/SNR)*bucket_yield_mean
    bucket_yields_list = []
    best_bucket_list = []
    weather_list = []
    one_third = N_buckets/3
    for idx in range(N_turns):
        weather = 'nominal'
        loc = bucket_yield_mean.copy()
        if (np.random.uniform(low=0.0, high=1.0) < 0.05):
            #upper two thirds of buckets are bad during story weather
            weather = 'stormy'
            loc[one_third:] *= -1.25
        if (np.random.uniform(low=0.0, high=1.0) < 0.05):
            #upper one thirds of buckets are worse during hot weather
            weather = 'hot'
            loc[2*one_third:] *= -1.4
        bucket_yields = np.random.normal(loc=loc, scale=bucket_yield_sigma)
        bucket_yields_list += [bucket_yields]
        best_bucket = np.zeros(N_buckets)
        best_idx = bucket_yields.argmax()
        best_bucket[best_idx] = 1.0
        best_bucket_list += [best_bucket]
        weather_list += [weather]
    actual_bucket_yields = np.array(bucket_yields_list)
    best_bucket = np.array(best_bucket_list)
    lagged_bucket_yields = np.roll(actual_bucket_yields, lag, axis=0)
    #onehot encode weather
    weather = np.array(weather_list)
    from sklearn.preprocessing import LabelEncoder
    encoder = LabelEncoder()
    encoder.fit(weather_list)
    weather_int = encoder.transform(weather_list)
    from keras.utils.np_utils import to_categorical
    weather_onehot = to_categorical(weather_int)
    return actual_bucket_yields, best_bucket, lagged_bucket_yields, weather, weather_onehot, \
        bucket_yield_mean, bucket_yield_sigma

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

#compute net_values generated by occupied buckets plus compounded net_value
#that uses trained model
def compute_net_value(actual_bucket_yields, lagged_bucket_yields, weather, weather_onehot, strategy, model=None):
    #compute bucket_occupation_fraction per strategy
    N_buckets = actual_bucket_yields.shape[1]
    bucket_occupation_fraction = np.zeros_like(actual_bucket_yields)
    one_third_buckets = N_buckets/3
    two_third_buckets = 2*one_third_buckets
    if (strategy == 'low'):
        bucket_occupation_fraction[:, 0:one_third_buckets] = 1.0
        bucket_occupation_fraction /= bucket_occupation_fraction[0].sum()
    if (strategy == 'middle'):
        bucket_occupation_fraction[:, one_third_buckets:two_third_buckets] = 1.0
        bucket_occupation_fraction /= bucket_occupation_fraction[0].sum()
    if (strategy == 'high'):
        bucket_occupation_fraction[:, two_third_buckets:] = 1.0
        bucket_occupation_fraction /= bucket_occupation_fraction[0].sum()
    if (strategy == 'random'):
        N_turns = actual_bucket_yields.shape[0]
        for idx in range(N_turns):
            random_bucket = np.random.randint(0, high=N_buckets)
            bucket_occupation_fraction[idx, random_bucket] = 1.0
    if (strategy == 'top'):
        bucket_occupation_fraction[:, -1] = 1.0
    if (strategy == 'smart'):
        x = np.concatenate((lagged_bucket_yields, weather_onehot), axis=1)
        bucket_occupation_fraction = model.predict(x)
    #compute net_values generated by occupied buckets
    cols = ['yield' + str(idx) for idx in range(N_buckets)]
    net_values = pd.DataFrame(actual_bucket_yields, columns=cols)
    net_values['net_value'] = 1.0
    for idx in range(N_buckets):
        occupation_prob_col = 'prob' + str(idx)
        net_values[occupation_prob_col] = bucket_occupation_fraction[:, idx]
        yield_col = 'yield' + str(idx)
        net_values['net_value'] += net_values[yield_col]*net_values[occupation_prob_col]
    #compute compounded value
    net_values['compound_value'] = net_values['net_value']
    for idx in range(len(net_values)):
        if (idx > 0):
            net_values.loc[idx, 'compound_value'] = \
                net_values.loc[idx, 'net_value']*net_values.loc[idx-1, 'compound_value']
    #add turn column
    net_values['turn'] = net_values.index
    #add weather
    net_values['weather'] = weather
    return net_values
