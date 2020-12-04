#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
"""
Created on Wed Jun 17 15:56:33 2020

@author: baptiste

Description: classes and simulation model definition
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import acf
import scipy.optimize as opt
from itertools import chain
from os.path import abspath, isfile, splitext
from datetime import datetime
import warnings

from . import __version__
from .io import read_csv

def _format_slice(slice_iter):
    """
    Convenient function to format `slice_iter` as a proper `slice` object.

    Parameters
    ----------
    slice_iter : None, int, tuple of 3 int or slice, optional
        Slicing to perform accross iterations, to decimate data.
        If None (default), no decimation.
        If int, decimation by step, starting after step (most common behavior)
        If 3-tuple, arguments are passed on to a slice object.
        If slice, this slice object is used to decimate.
    
    Returns
    -------
    idx : slice
        Sliced arrangement, to pass to sliceable object.
    """
    if slice_iter is None:
        idx = slice(None)
    elif isinstance(slice_iter, int):
        idx = slice(slice_iter, None, slice_iter)
    elif isinstance(slice_iter, tuple) and (len(slice_inter) == 3):
        idx = slice(*slice_iter)
    elif isinstance(slice_iter, slice):
        idx = slice_iter
    else:
        raise TypeError('`slice_error` argument improperly handled, read'\
                +' `._format_slice` docstring.')
    return idx


class Bubble:
    """
    A bubble in the simulation.

    Attributes 
    ----------
    Attributes are flexible, and depend on each simulation requirements.
    They are defined at instantiation as keyword arguments.

    Methods
    -------
    to_dict : return attributes as a dictionary.

    to_series : return attributes as a pandas.Series.
    """
    def __init__(self, **kwargs):
        """
        kwargs : keyword arguments, passed on as class attributes.
        """
        for k, v in kwargs.items():
            self.__setattr__(k, v)
        return

    def to_dict(self):
        """
        Return bubble info as a dictionary.
        """
        return self.__dict__

    def to_series(self):
        """
        Return bubble info as a pd.Series.
        """
        return pd.Series(self.__dict__)


class BaseSimu:
    """
    Meta-class for collective surface bubbles simulations.

    Children must define the following methods and attributes.
    Attributes
    ----------
    `_bubbles` : list
        List of **current** bubbles, carried on all along the simulation. Can 
        contain as little information as the bubbles radii or volumes, or their
        location, etc. The dimensionality must match that of the methods 
        modifying it.

    `bubbles` : list
        List of bubbles dumped after every iteration. See also `_format_bubbles`.

    `params` : dict
        Simulation parameters. See also `params_df`.

    `_bubble_init` : dict
        Bubble initialization properties.
 
    Numerical Methods
    -----------------
    `step_advance(bubbles)`
        Step advance, defined as the sequence of the 4 methods (create, pop,
        move, merge), in this order. When bubbles have a lifetime, it is 
        incremented by 1 after those.

    `run(n_steps)`
        Advance simulation by `n_steps`.

    The following methods are sub-class dependent, and have to be (re)-defined
    and overridden.
    `_create_bubbles(bubbles)`
        Create/introduce bubbles.

    `_pop_bubbles(bubbles)` 
        Pop/burst bubbles.

    `_move_bubbles(bubbles)` 
        Move/displace bubbles.

    `_merge_bubbles(bubbles)` 
        Merge/coalesce bubbles.

    `_format_bubbles(bubbles)` 
        Format bubbles, before appending to `bubbles`.

    Other Methods
    -------------
    `plot_bubbles_number()`
        Plot bubbles number vs iteration.

    `_count_bubbles(bubbles)`
        Count bubbles (may require more elaborate procedure than `len(bubbles)`)

    `to_hdf(filename)`
        Export bubbles as HDF5 file (using pandas).
    """
    def __init__(self, **kw_params):
        """
        Parameters
        ----------
        data_id : None or tuple, optional
            Data identifier, to proceed to

        **kw_params : keyword arguments
            Additional parameters.
        """
        # initialize parameters
        from .main import _params_default, _bubble_init
        # module default values
        self.params = _params_default.copy()
        self.params['code_version'] = __version__
        self.params['class_name'] = '.'.join((self.__module__, self.__name__))
        self.params['timestamp'] = datetime.now()
        # class default values
        if hasattr(self, '_params_default'):
            for k, v in self._params_default.items():
                self.params[k] = v
        # keyword arguments values
        for k, v in kw_params.items():
            self.params[k] = v

        # init bubbles
        _init = _bubble_init.copy()
        if hasattr(self, '_bubble_init'):
            for k, v in self._bubble_init.items():
                _init[k] = v
        self._bubble_init = _init
        if 'bubbles' in kw_params:
            bubbles = kw_params['bubbles']
            del self.params['bubbles']
        else:
            bubbles = [Bubble(**_init)\
                for i in range(self.params['n_bubbles'])]
        self._bubbles = bubbles
        self.bubbles = [self._format_bubbles(bubbles)]
        return None

    @property
    def params_df(self):
        """Simulation parameters as a pandas.Series"""
        return pd.Series(self.params)

    def __len__(self):
        return len(self.bubbles)

    def step_advance(self, bubbles):
        """
        Advance simulation by 1 iteration.

        Parameters
        ----------
        bubbles : list
            Current list of bubbles.

        Returns
        -------
        bubbles : list
            Updated list of bubbles.

        Notes
        -----
        Apply methods in the following order:
        1. `_new_bubbles(bubbles)`
        2. `_pop_bubbles(bubbles)`
        3. `_move_bubbles(bubbles)`
        4. `_merge_bubbles(bubbles)`
        """
        # produce new bubbles
        bubbles = self._create_bubbles(bubbles)
        # burst bubbles
        bubbles = self._pop_bubbles(bubbles)
        #TODO: bubbles move a little around their location (needs dynamics)
        bubbles = self._move_bubbles(bubbles)
        bubbles = self._merge_bubbles(bubbles)
        if 'lifetime' in self._bubble_init:
            for b in bubbles:
                b.lifetime += 1
        return bubbles

    def run(self, steps=None):
        """
        Run simulation for given number of steps.
        """
        bubbles = self._bubbles
        if steps is None:
            steps = self.params['steps']
        for n in range(steps):
            bubbles = self.step_advance(bubbles)
            self.bubbles.append(self._format_bubbles(bubbles))
        return None

    def plot_bubbles_number(self, ax=None):
        """
        Plot ``time'' series for length of bubbles list at each iteration.

        Parameters
        ----------
        ax : None or plt.Axes, optional
            Where to display plot.
        """
        bubbles = self.bubbles.copy()
        if ax is None:
            fig, ax = plt.subplots()
        ax.set_ylabel('Count')
        ax.set_xlabel('Iteration')
        ax.set_xlim(0, len(bubbles))
        l = ax.plot([self._count_bubbles(b) for b in bubbles], label='$N$')
        ax.set_ylim(bottom=0)
        return ax

    def to_hdf(self, fname, **kwargs):
        """
        Save data to .h5 file.

        Parameters
        ----------
        fname : str
            File name.
        
        **kwargs : keywords arguments passed on to `df.to_hdf`. Default values
            are `key='df', mode='a'`.
        """
        df = pd.concat({i: pd.DataFrame(d)\
                for i, d in enumerate(self.bubbles)}, \
                names=['iter', 'bubbles'])
        if 'key' not in kwargs.keys():
            kwargs['key'] = 'df'
        df.to_hdf(fname, **kwargs)
        return None

    def _count_bubbles(self, bubbles):
        """
        Count bubbles.

        Parameters
        ----------
        bubbles : list
            List of bubbles.

        Returns
        -------
        N : int
            Bubbles count.

        Notes
        -----
        Used in `plot_bubbles_number`, and should be overridden to match the 
        way bubbles are saved in `self.bubbles`.
        """
        return len(bubbles)
    
    def _create_bubbles(self, bubbles):
        """
        Create bubbles method.

        Parameters
        ----------
        bubbles : list
            List of current bubbles.

        Returns
        -------
        bubbles : list
            (Updated) list of current bubbles.
        """
        return bubbles

    def _pop_bubbles(self, bubbles):
        """
        Pop/burst bubbles method.

        Parameters
        ----------
        bubbles : list
            List of current bubbles.

        Returns
        -------
        bubbles : list
            (Updated) list of current bubbles.
        """
        return bubbles

    def _move_bubbles(self, bubbles):
        """
        Move bubbles method.

        Parameters
        ----------
        bubbles : list
            List of current bubbles.

        Returns
        -------
        bubbles : list
            (Updated) list of current bubbles.
        """
        return bubbles

    def _merge_bubbles(self, bubbles):
        """
        Merge bubbles method.

        Parameters
        ----------
        bubbles : list
            List of current bubbles.

        Returns
        -------
        bubbles : list
            (Updated) list of bubbles.
        """
        return bubbles

    def _dump_bubbles(self, bubbles):
        """
        **Copy** & format bubbles before dumping/exporting/saving in `bubbles`.

        Parameters
        ----------
        bubbles : list
            Current list of bubbles.

        Returns
        -------
        bubbles_fmt : pd.DataFrame, list, pd.Series, np.array
            Your choice of format before saving. Be sure to copy the data in
            some way.

        Notes
        -----
        Called at every iteration by `self.run`.
        """
        return bubbles.copy()


class SimuVolumesInt(BaseSimu):
    """
    More specific data handling, which defines corresponding plot, export, etc.
    functions.

    Parameters
    ----------
    mode : None or str, optional
        When None, chooses automatically between the available options:
        - `run` to run simulation (includes resuming simulation, default)
        - `analysis` to analyze data (does not rebuild list of bubbles, default
            mode when loading data)

    Notes
    -----
    Physics is based on distribution of diameter, which determines everything.
    The only info stored is then the ***VOLUME*** distribution, volume being
    kept as integer. The translation to diameters is done via the attribute
    `d_unit`.
    
    
    Data storage
    ------------
    Data is stored as HDF (extension .h5) files. The key `count` contains a
    `pd.Series` with bubble volume counts for each iteration: pd.MultiIndex
    `iter, volume`. Iteration with no bubbles are artificially saved as 0 
    bubbles with volume 1.

    csv takes less space than HDF5: a way of remediating this would be to
    change 'int64' to 'int8', when possible.
    """
    def __init__(self, mode=None, **kwargs):
        super().__init__(**kwargs)
        self.mode = 'run'
        if 'filename' in kwargs:
            fname = abspath(kwargs['filename'])
            self.params, df = self._read_file(fname)

            if mode is None or mode == 'analysis':
                self.bubbles = df
                self._bubbles_df = df
                self.mode = 'analysis'
            elif mode == 'run':
                # THIS LINE TAKES TOO LONG (and useless unless wanna keep running
                # simulation, but there are other ways to do)
                self.bubbles = [df.loc[k] \
                        for k in df.index.get_level_values(0).unique()]
                self.mode = 'run'
            self._bubbles = list(chain(*[r*[k] \
                    for k, r in df.loc[df.index[-1][0]].iteritems()]))
            
        return None

    @staticmethod
    def _read_file(fname):
        if isfile(fname):
            ext = splitext(fname)[-1]
            if ext == '.h5':
                with pd.HDFStore(fname, mode='r') as store:
                    df = store['count']
                    try:
                        params = store.get_storer('count').attrs['params']
                    except KeyError:
                        params = store['params']
                        msg = 'Params saved before v0.2., '\
                                +'may need some harmonizing.'
                        warnings.warn(msg, UserWarning)
                if df.dtype != 'int64':
                    # TODO: maybe harmonize everything in UINT64? No need.
                    df = df.astype('int64')
            elif ext == '.csv':
                params, df = read_csv(fname, index_col=(0, 1))
                df = df['count']
        return params, df

    def _format_bubbles(self, bubbles):
        """
        Notes
        -----
        This is the function that makes the specificity of this class: bubbles
        are formatted as pairs of `volume (as int): number`.
        """
        V = [b.volume for b in bubbles]
        dic = dict(zip(*np.unique(V, return_counts=True)))
        return dic

    def _count_bubbles(self, bubbles):
        return sum(bubbles.values())

    @property
    def bubbles_df(self):
        """
        Bubbles as a DataFrame.

        Notes
        -----
        DataFrame is computed at first call, then stored in private attribute
        `_bubbles_df`, and updated at next call, if new bubbles computed.
        """
        if self.mode == 'analysis':
            # bubbles are already a DF. BEWARE it's not a copy!
            df = self._bubbles_df
        elif self.mode == 'run':
            # else concat from the list of dict
            df = self._get_bubbles_df()
        return df

    def _get_bubbles_df(self):
        """Compute or update bubbles as DataFrame."""
        if hasattr(self, '_bubbles_df'):
            # Compare with length of simulation
            n = len(self._bubbles_df.index.get_level_values('iter').unique())
            if n < len(self):
                # If smaller, update with new bubbles
                df2 = pd.concat({n+i: pd.Series(b, name='count')\
                        for i, b in enumerate(self.bubbles[n:])},\
                        names=['iter', 'volume'])
                df = pd.concat((self._bubbles_df, df2))
            else:
                # else it's just it!
                df = self._bubbles_df
        else:
            # First computation of the DF
            df = pd.concat(dict(enumerate(\
                    pd.Series(b, name='count')\
                    for b in self.bubbles)),
                    names=['iter', 'volume'])
        # store DF in a private variable
        self._bubbles_df = df
        return df

    def __len__(self):
        if self.mode == 'run':
            l = super().__len__()
        elif self.mode == 'analysis':
            l = len(self.bubbles.index.get_level_values('iter').unique())
        return l

    def to_hdf(self, fname, mode='w'):
        """
        Save bubble volume distribution/count (per iteration) as HDF5 file.
        
        Parameters
        ----------
        fname : str
            Filename.

        mode : str, optional
            Python open file mode.

        Notes
        -----
        * HDF5 file contain 1 key: `count`, i.e. 1 table where Series of bubbles
        counts are stored (hierarchical index iteration/volume (as int)).
        * Parameters `params` are saved as an attribute of the corresping table.
        * When bubbles count per iteration is less than 2**8 (resp. 16, 32),
        data is saved as UINT8 (resp. 16, 32).

        See also
        --------
        _read_file : `filename` keyword argument to retrieve stored data.
        """
        df = self.bubbles_df.copy()
        nmax = df.max()
        # choose dtype to minimize storage
        if nmax < 2**8:
            dtype = 'uint8'
        elif nmax < 2**16:
            dtype = 'uint16'
        elif nmax < 2**32:
            dtype = 'uint32'
        else:
            dtype = df.dtype
        with pd.HDFStore(fname, mode=mode) as store:
            key = 'count'
            # store data, then parameters as attribute
            store.put(key, df.astype(dtype))
            store.get_storer(key).attrs.params = self.params
        return
        
    def to_csv(self, fname, header_tag='params', **kwargs):
        """
        Save bubble volume distribution/count (per iteration) as CSV file.
        
        Notes
        -----
        * Existing file is overridden.
        * A header containing the simulation parameters is written between
            html-like tags `<header_tag>` and `</header_tag>`, one per line
            as key-value pairs, separated by `sep`.
        
        See also
        --------
        __init__ : `filename` keyword argument to retrieve stored data.
        """
        if 'sep' in kwargs:
            sep = kwargs['sep']
        else:
            sep = ','
        # format and save header
        lines = ['{}{}{}\n'.format(k, sep, v) for k, v in self.params.items()]
        with open(fname, 'w') as f:
            f.write('<{}>\n'.format(header_tag))
            f.writelines(lines)
            f.write('</{}>\n'.format(header_tag))
        self.bubbles_df.to_csv(fname, mode='a', **kwargs)
        return None

    def plot_time_series(self, cols=['count', 'avg_d^1']):
        """
        Quick plot of `self.bubbles_by_iter`.
        """
        w, h = plt.rcParams['figure.figsize']
        fig, axs = plt.subplots(len(cols), 1, sharex=True, 
                tight_layout=False,
                figsize=[w, len(cols)*h*.5])
        fig.subplots_adjust(hspace=0)
        bubbles = self.bubbles_by_iter.copy()
        labels = {
                'count': r'$n$', 
                'avg_d^1': r'$\langle d/d_1 \rangle$',
                'avg_d^2': r'$\langle d^2/d_1^2 \rangle$',
                'avg_d^3': r'$\langle d^3/d_1^3 \rangle$',
                }
        # count
        for c, ax in zip(cols, axs):
            ax.plot(bubbles[c], 'k-')
            ax.set_ylabel(labels[c])
            ax.set_ylim(bottom=0)
        ax.set_xlabel('Iteration')
        ax.set_xlim(0, len(bubbles))
        return None

    def acf(self, cols=['count', 'avg_d^1'], ax=None, **kw_acf):
        """
        Compute and plot auto-correlation function (ACF).

        Parameters
        ----------
        cols : list of str, optional
            List of columns in `self.bubbles_by_iter` to consider.

        ax : bool or plt.Axes, optional
            Whether, and where to plot ACF.

        Returns
        -------
        taus : pd.DataFrame
            Fitted decay times.

        See also
        --------
        statsmodels.tsa.stattools.acf: Auto-correlation function.
        """
        # Init process and kwargs
        bubbles = self.bubbles_by_iter.copy()
        if 'fft' not in kw_acf.keys():
            kw_acf['fft'] = True
        if 'missing' not in kw_acf.keys():
            kw_acf['missing'] = 'drop'
        if 'nlags' not in kw_acf.keys():
            nlags = 40
            kw_acf['nlags'] = nlags
        else:
            nlags = kw_acf['nlags']
        # init plot
        t = np.arange(nlags+1)
        t_opt = {}
        y_acf = pd.DataFrame([], columns=cols, index=t)
        for c in cols:
            # compute auto-correlation function
            y = acf(bubbles[c].values, **kw_acf)
            # and fit exponential decay
            tau = opt.curve_fit(lambda t, tau: np.exp(-t/tau), t, y)
            t_opt[c] = np.r_[tau[0], np.sqrt(np.diag(tau[1]))]
            y_acf[c] = y
        # plot
        if ax is not None:
            t_exp = np.linspace(0, nlags, 10*nlags)
            if not isinstance(ax, plt.Axes):
                fig, ax = plt.subplots()
            for c in cols:
                l, = ax.plot(t, y_acf[c], 'o')
                ax.plot(t_exp, np.exp(-t_exp/t_opt[c][0]), '-',\
                        color=l.get_color())
                l, = ax.plot([], 'o-', color=l.get_color(), label=c)
            ax.legend(loc='upper right')
            ax.set_xlabel('Lag')
            ax.set_ylabel('ACF')
            ax.set_xlim(0, nlags)
            ax.set_ylim(-.2, 1)
        t_opt = pd.DataFrame(t_opt, index=['tau_opt', 'tau_err']).T
        return t_opt

    @property
    def bubbles_by_iter(self, moments=[1, 2, 3]):
        """Bubbles properties per iteration.

        Parameters
        ----------
        moments : iterable, optional
            Moments of bubble diameter :math: `d = k**(1/3)` to compute.

        Returns
        -------
        bubbles : pd.DataFrame
            Data for each iteration.

        Notes
        -----
        Moments of bubble diameter are computed in 3 steps:
        - retrieve bubble diameter :math: `d = k**(1/3)`, with `k` its integer
            volume
        - compute the weighted quantities `n_k d^p`.
        - group by iteration and sum, taking advantage of `pandas` fast
            aggregation.
        """
        if hasattr(self, '_bubbles_by_iter')\
                and len(self._bubbles_by_iter) == len(self):
            return self._bubbles_by_iter
        # get DF
        b = self.bubbles_df.reset_index()
        cols = ['count']
        for p in moments:
            # prepare weighted sum
            c = 'sum_n_d^{}'.format(p)
            b[c] = b['count']*b['volume']**(p/3)
            cols.append(c)
        # group DF by iteration, dropping volume column, and aggregate by sum
        gr = b.groupby('iter')[cols]
        by_iter = gr.sum()
        # compute actual moments (divide by the number of events)
        for p in moments:
            c = '_d^{}'.format(p)
            by_iter['avg'+c] = by_iter['sum_n'+c]/by_iter['count']
        self._bubbles_by_iter = by_iter
        return by_iter

    def get_histogram(self, slice_iter=None, ax=None):
        """
        Get counts of each volume, accross given iterations.

        Parameters
        ----------
        slice_iter : None, int, tuple of 3 int or slice, optional
            See `_format_slice` docstring in this module.

        ax : bool or plt.Axes, optional
            Plot histogram.

        Returns
        -------
        counts : pd.Series
            Counts/histogram of bubble volume accross given iterations.
        """
        #TODO: implement iter selection
        idx = _format_slice(slice_iter)
        bubbles = self.bubbles_df.loc[idx, slice(None)].copy()
        counts = bubbles.groupby('volume').apply(sum)
        if ax is not None:
            if not isinstance(ax, plt.Axes):
                fig, ax = plt.subplots()
            counts.plot(ax=ax, marker='o', ls='')
            ax.set_xscale('log')
            ax.set_yscale('log')
        return counts

    def get_moments(self, slice_iter=None):
        """
        Get moments of the bubbles distribution for the given iterations.

        Parameters
        ----------
        slice_iter : None, int, tuple of 3 int or slice, optional
            See `_format_slice` docstring in this module.

        Notes
        -----
        Moments are named after the physical properties they are related to,
        but they are NOT scaled accordingly (in particular the bubble size is
        taken as `volume**(1/3)`):
        - 0: total `count` of bubbles accross iterations. Need to normalize by
            number of iterations and surface area to get density.
        - 1: mean diameter, in units of `self.d_unit`.
        - 2: to get surface area `coverage` by bubbles, normalize by number of
            iterations, surface area and `pi/4*self.d_unit**2`.
        - 3: volumes are in natural units (integers).
        """
        # 2 methods: either by iter first, then average, or average directly
        h = self.get_histogram(slice_iter=slice_iter).reset_index()
        d = h['volume']**(1/3)
        n = h['count']
        moments = pd.Series({
            '0_count': int(np.sum(n)),
            '1_d_avg': np.average(d, weights=n),
            '2_coverage': np.average(d**2, weights=n),
            '3_volume': np.average(d**3, weights=n),
            }, name='moments')
        return moments



