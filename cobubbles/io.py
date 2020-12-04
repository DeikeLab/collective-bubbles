#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
#
#File name: io.py
#Author: Baptiste Neel
#Creation date: 28-04-2020
#Description:

import pandas as pd
from datetime import datetime

dtypes = {
        'int': ['steps', 'n_bubbles', 'rate_prod_avg', 'rate_prod_std'],
        'str': ['code_version', 'class_name'],
        'float': ['width', 'mean_lifetime', 'merging_probability', 'meniscus'],
        'datetime': ['timestamp'],
        }

convert = {
        'int': lambda x: int(x),
        'float': lambda x: float(x),
        'str': lambda x: x,
        'datetime': lambda x: datetime.fromisoformat(x),
        }

class DataFormatError(Exception):
    pass

def read_hdf(fname, **kwargs):
    """Read HDF5 bubbles file"""
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

def read_csv(fname, header_tag='params', **kwargs):
    """
    Read CSV bubbles file with header.

    Parameters
    ----------
    fname : str
        Filename.

    header_tag : str or None, optional
        If a string is provided, sparse the header contained between
        html-style tags `<header_tag>` and `</header_tag>`.

    **kwargs : keyword arguments passed on to `pd.read_csv`.

    Returns
    -------
    params : dict
        Dictionary with header values returned as a dictionary.

    df : pd.Series or pd.DataFrame
        Bubbles counts, per iteration.

    See also
    --------
    to_csv methods in corresponding classes.
    parse_header
    """
    if header_tag is not None:
        if 'sep' in kwargs:
            sep = kwargs['sep']
        else:
            sep = ','
        params = parse_header(fname, header_tag, sep)
        n = len(params)+2
    else:
        params = None
        if 'skiprows' in kwargs:
            n = kwargs['skiprows']
        else:
            n = 0
    df = pd.read_csv(fname, skiprows=n, **kwargs)
    return params, df

def parse_header(fname, header_tag, sep=','):
    """
    Parse header on a text file (CSV primarily).

    Parameters
    ----------
    fname : str
        Filename.

    header_tag : str or None, optional
        If a string is provided, sparse the header contained between
        html-style tags `<header_tag>` and `</header_tag>`.

    sep : str, optional
        Key-value separator. Default to CSV default.

    Returns
    -------
    params : dict
        Parameters contained in the header, converted to the proper data type.

    See also
    --------
    `dtypes` and `convert`: handling of data type conversion. 
    """
    params = {}
    with open(fname, 'r') as f:
        l = f.readline()
        if l[1:-2] != header_tag:
            raise DataFormatError('Mismatching header tag.')
        end = '</{}>\n'.format(header_tag)  # end tag
        while l != end and l != '':
            # read header lines
            l = f.readline()
            if l != end:
                # and format and convert to desired dtype
                k, v = l[:-1].split(sep)
                dtype = [x for x, y in dtypes.items() if k in y][0]
                params[k] = convert[dtype](v)
    return params
    
