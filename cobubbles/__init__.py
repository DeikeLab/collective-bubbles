#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
#
#Author: Baptiste Neel
#Creation date: 13-04-2020
#Description:

import pandas as pd
from os.path import abspath, join
import os

to_Int64 = ['steps', 'meniscus', 'acf_tau']

home = abspath(os.environ['HOME'])
if home == abspath('/home/baneel'):
    base = abspath('/media/baneel/StorageA')
elif home == abspath('/Users/baptiste'):
    base = home
folder = join(base, 'Dropbox (Princeton)', 'Share', 'bubbles_model')

DIRS = {
        'data': join(folder, 'data'),
        'cwd': folder, 
        }

DATA = pd.read_csv(join(folder, 'data.csv'), \
        index_col=['date', 'run'])
for c in to_Int64:
    DATA[c] = DATA[c].astype('Int64')

del home, base, folder

