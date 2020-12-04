#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
#
#File name: io.py
#Author: Baptiste Neel
#Creation date: 28-04-2020
#Description:

import pandas as pd
from datetime import datetime
import warnings

dtypes = {
        'int': ['steps', 'n_bubbles', 'rate_prod_avg', 'rate_prod_std'],
        'str': ['code_version', 'class_name', 'timestamp'],
        'float': ['width', 'mean_lifetime', 'merging_probability', 'meniscus'],
        }

convert = {
        'int': lambda x: int(x),
        'float': lambda x: float(x),
        'str': lambda x: x,
        }

class DataFormatError(Exception):
    pass

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
    
def read_hdf(fname, key='count', params_prefix='params', **kwargs):
    """
    Read HDF5 bubbles counts file.

    Parameters
    ----------
    fname : str
        filename

    key : str, optional
        Key for data.

    params_prefix : str, optional
        Prefix for parameters, saved as attributes of fetched table. Does not
        need the separator (usually `_`).
        
    **kwargs : keyword arguments passed on to Python file `open`.

    Returns
    -------
    params : dict
        Dictionary with header values returned as a dictionary.

    df : pd.Series or pd.DataFrame
        Bubbles counts, per iteration.
    """
    # open store
    with pd.HDFStore(fname, **kwargs) as store:
        # retrieve DF
        df = store[key]
        # fetch attributes
        attrs = store.get_storer(key).attrs
        params = {k[len(params_prefix)+1:]: attrs[k] \
                for k in attrs._v_attrnames\
                if k.startswith(params_prefix)}
        if len(params) == 0:
            # if no parameters saved, try to retrieve them from another table
            params = store[params_prefix]
            msg = 'Params saved before v0.2., '\
                    +'may need some data type harmonizing.'
            warnings.warn(msg, UserWarning)
    return params, df

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

