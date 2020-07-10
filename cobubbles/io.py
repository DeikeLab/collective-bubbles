#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
#
#File name: io.py
#Author: Baptiste Neel
#Creation date: 28-04-2020
#Description:

import pandas as pd

def read_hdf(fname, **kwargs):
    if 'key' not in kwargs.keys():
        kwargs['key'] = 'df'
    df = pd.read_hdf(fname, **kwargs)
    return df

def groupby_iter(df):
    bubbles = df.reset_index().groupby('iter')
    by_iter = pd.DataFrame([], index=bubbles.groups.keys(),
            columns=['d_avg', 'count'])
    for k, b in bubbles:
        by_iter.loc[k, 'count'] = np.sum(b['count'])
        if np.sum(b['count']) > 0:
            by_iter.loc[k, 'd_avg'] = np.average(
                    b['volume']**(1/3)*self.d_unit, weights=b['count'])
    return by_iter

