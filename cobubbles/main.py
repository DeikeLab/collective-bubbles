"""Module main.py

Description: Definition of different simulations.

Created on Wed Apr 8 15:56:33 2020

@author: baptiste

"""

import numpy as np
from scipy import stats, special
import importlib as imp
from os.path import split, join, splitext
from math import pi

from . import classes
imp.reload(classes)
from .classes import SimuVolumesInt, Bubble
from .methods_merge import merge_bubbles_closest

## DEFAULT NUMERICAL SETTINGS & PHYSICAL CONSTANTS
# TODO: move class-specific parameters in respective class definition
_params_default = {
        'steps': 100,   #simu length
        'width': 30,    #box size
        'n_bubbles': 1,    #initial number of bubbles
        'rate_prod_avg': 16,    #bubble production rate, normal distribution
        'rate_prod_std': 4,
        'meniscus': 1,  #meniscii interaction length
        }

_bubble_init = {
        'diameter': 1,
        'volume': 1,
        'age': 0,
        }


class SimuA(SimuVolumesInt):
    """
    First automaton implemented, deprecated.
    No mean lifetime, bubbles have no age, they are just popped from the list
    randomly, at a given rate.

    Creation: `rate_prod` bubbles per iteration (`_avg` +/- `_std`).

    Bursting: remove `rate_pop` bubbles per iteration (`_avg` +/- `_std`).
    """
    __name__ = 'SimuA'
    __warnings__ = [
            (DeprecationWarning, 'Improper handling of bursting, use `SimuD` instead'),
            ]
    _params_default = {
            'd_unit': (6/pi)**(1/3),
            'rate_pop_avg': 10, 
            'rate_pop_std': 2,
            }

    def _create_bubbles(self, bubbles):
        """
        Append `n` bubbles of unit size, where `n` is normally distributed.
        """
        q_prod = [self.params['rate_prod_'+s] for s in ['avg', 'std']]
        n_new = abs(int(round(stats.norm.rvs(*q_prod))))
        bubbles += [Bubble(**self._bubble_init) for i in range(n_new)]
        return bubbles

    def _pop_bubbles(self, bubbles):
        """
        Pop `n` bubbles, randomly (uniform distribution) chosen in the bubbles
        list. `n` is normally distributed.
        Notes
        -----
        Currently implemented: only uniform popping for every sizes.
        """
        q_pop = [self.params['rate_pop_'+s] for s in ['avg', 'std']]
        n_pop = min((len(bubbles),\
                abs(int(round(stats.norm.rvs(*q_pop))))))
        for k in sorted(np.unique(np.random.randint(len(bubbles), size=n_pop)),\
                        reverse=True):
            bubbles.pop(k)
        # TODO: implement Villermaux pop formula
        return bubbles 

    def _move_bubbles(self, bubbles):
        """
        Scatter bubbles uniformly in a square box.
        Notes
        -----
        This initialisation is of a Markov-kind, in the sense that it disregards
        the dynamics and history of the bubbles.
        """
        for b in bubbles:
            b.xy = np.random.rand(2)*self.params['width']
        return bubbles

    def _merge_bubbles(self, bubbles):
        """
        Merge bubbles, closest first.
        """
        # if no bubbles, jump to next iteration
        p = self.params
        if len(bubbles) >= 2:
        # scheme: closest merge first
            bubbles = merge_bubbles_closest(bubbles, p['meniscus'])
        return bubbles
        #TODO: below threshold, pick pairs randomly
        #TODO: implement multi-merging in same step
        return bubbles


class SimuB(SimuVolumesInt):
    """
    Creation: `rate_prod` bubbles per iteration.

    Bursting: remove old bubbles, according to Weibull distribution of 
        lifetimes.
    """
    __name__ = 'SimuB'
    __warnings__ = [
            (UserWarning, 'Improper handling of bursting, use `SimuD` instead'),
            ]
    _params_default = {
            'mean_lifetime': 1,
            'merging_probability': 1,
            }

    _bubble_init = {
            }

    def _create_bubbles(self, bubbles):
        """
        Append `n` bubbles of unit size, where `n` is normally distributed.
        """
        q_prod = [self.params['rate_prod_'+s] for s in ['avg', 'std']]
        n_new = abs(int(round(stats.norm.rvs(*q_prod))))
        bubbles += [Bubble(**self._bubble_init) for i in range(n_new)]
        return bubbles

    def _pop_bubbles(self, bubbles):
        """
        Pop `n` bubbles, randomly (uniform distribution) chosen in the bubbles
        list. `n` is normally distributed.
        Notes
        -----
        Currently implemented: only uniform popping for every sizes.
        """
        p = stats.weibull_min.cdf([b.age for b in bubbles],\
                4/3, loc=0, scale=self.params['mean_lifetime'])
        pop, = np.where(np.random.binomial(1, p) == 1)
        for k in sorted(pop, reverse=True):
            bubbles.pop(k)
        return bubbles

    def _move_bubbles(self, bubbles):
        for b in bubbles:
            b.xy = np.random.rand(2)*self.params['width']
        return bubbles

    def _merge_bubbles(self, bubbles):
        p = self.params
        if len(bubbles) >= 2:
        # scheme: closest merge first
            bubbles = merge_bubbles_closest(bubbles, p['meniscus'],
                    proba=p['merging_probability'])
        return bubbles


class SimuB2(SimuB):
    """
    Creation: `rate_prod` bubbles per iteration.

    Bursting: remove old bubbles, according to exponential distribution of 
        lifetimes.
    """
    __name__ = 'SimuB2'
    _params_default = {
            'mean_lifetime': 1,
            'merging_probability': 1,
            }

    _bubble_init = {
            }

    def _pop_bubbles(self, bubbles):
        """
        Pop `n` bubbles, randomly (uniform distribution) chosen in the bubbles
        list. `n` is normally distributed.
        Notes
        -----
        Currently implemented: only uniform popping for every sizes.
        """
        p = stats.expon.cdf([b.age for b in bubbles],\
                loc=0, scale=self.params['mean_lifetime'])
        pop, = np.where(np.random.binomial(1, p) == 1)
        for k in sorted(pop, reverse=True):
            bubbles.pop(k)
        return bubbles


class SimuC(SimuVolumesInt):
    """
    Creation: `rate_prod` bubbles per iteration.

    Bursting: remove bubbles older than `age`.
    """
    __name__ = 'SimuC'
    _params_default = {
            'lifetime': 1,
            'merging_probability': 1,
            }

    _bubble_init = {
            }

    def _create_bubbles(self, bubbles):
        """
        Append `n` bubbles of unit size, where `n` is normally distributed.
        """
        q_prod = [self.params['rate_prod_'+s] for s in ['avg', 'std']]
        n_new = abs(int(round(stats.norm.rvs(*q_prod))))
        bubbles += [Bubble(**self._bubble_init) for i in range(n_new)]
        return bubbles

    def _pop_bubbles(self, bubbles):
        """
        Pop `n` bubbles, randomly (uniform distribution) chosen in the bubbles
        list. `n` is normally distributed.
        Notes
        -----
        Currently implemented: only uniform popping for every sizes.
        """
        pop, = np.where(
                np.r_[[b.age for b in bubbles]] > self.params['lifetime'])
        for k in sorted(pop, reverse=True):
            bubbles.pop(k)
        return bubbles

    def _move_bubbles(self, bubbles):
        for b in bubbles:
            b.xy = np.random.rand(2)*self.params['width']
        return bubbles

    def _merge_bubbles(self, bubbles):
        p = self.params
        if len(bubbles) >= 2:
        # scheme: closest merge first
            bubbles = merge_bubbles_closest(bubbles, p['meniscus'],
                    proba=p['merging_probability'])
        return bubbles


class SimuD(SimuVolumesInt):
    """
    Bubbles are assigned a lifetime when created, random according to the given
    `dist_lifetime` distribution.
    Bub

    Intended to replace `SimuB`.

    Notes
    -----
    Consider deriving SimuD with no move, no merge, to study just bursting.
    """
    __name__ = 'SimuD'
    _params_default = {
            'dist_lifetime': stats.weibull_min(4/3, loc=0, \
                    scale=10/special.gamma(7/4)),#LV2012
            #'dist_lifetime': stats.expon(loc=0, scale=10),
            'n_bubbles': 0,
            'merging_probability': 1,
            }
    _bubble_init_ = {'age' : 0}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        n0 = self.params['n_bubbles']
        if 'filename' not in kwargs and n0 > 0:
            tau = self.params['dist_lifetime'].rvs(size=n0)
            for b, t in zip(self._bubbles, tau):
                b.lifetime = t
        return

    def _create_bubbles(self, bubbles):
        q_prod = [self.params['rate_prod_'+s] for s in ['avg', 'std']]
        n_new = abs(int(round(stats.norm.rvs(*q_prod))))
        # assign random lifetime at bubble creation
        tau = self.params['dist_lifetime'].rvs(size=n_new)
        bubbles += [Bubble(lifetime=t, **self._bubble_init) for t in tau]
        return bubbles

    def _move_bubbles(self, bubbles):
        for b in bubbles:
            b.xy = np.random.rand(2)*self.params['width']
        return bubbles

    def _merge_bubbles(self, bubbles):
        p = self.params
        n = len(bubbles)
        if n >= 2:
        # scheme: closest merge first
            bubbles = merge_bubbles_closest(bubbles, p['meniscus'],
                    proba=p['merging_probability'], age=0)
            #assign lifetime to bubble
            n_new = n - len(bubbles)
            tau = p['dist_lifetime'].rvs(size=n_new)
            for b, t in zip(bubbles[::-1], tau):
                if hasattr(b, 'lifetime'):
                    m = 'Merged bubble lifetime already defined.'
                    raise NotImplementedError(m)
                b.lifetime = t
        return bubbles

    def _pop_bubbles(self, bubbles):
        # burst bubbles that are older than their lifetime
        eol = np.r_[[b.age - b.lifetime for b in bubbles]]
        pop, = np.where(eol >= 0)
        for k in sorted(pop, reverse=True):
            bubbles.pop(k)
        return bubbles


