"""Module main.py

Description: Definition of different simulations.

Created on Wed Apr 8 15:56:33 2020

@author: baptiste

"""

import numpy as np
from scipy import stats
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
    _params_default = {
            'mean_lifetime': 1,
            'merging_probability': 1,
            }

    _bubble_init = {
            'lifetime': 0,
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
        p = stats.weibull_min.cdf([b.lifetime for b in bubbles],\
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
            'lifetime': 0,
            }

    def _pop_bubbles(self, bubbles):
        """
        Pop `n` bubbles, randomly (uniform distribution) chosen in the bubbles
        list. `n` is normally distributed.
        Notes
        -----
        Currently implemented: only uniform popping for every sizes.
        """
        p = stats.expon.cdf([b.lifetime for b in bubbles],\
                loc=0, scale=self.params['mean_lifetime'])
        pop, = np.where(np.random.binomial(1, p) == 1)
        for k in sorted(pop, reverse=True):
            bubbles.pop(k)
        return bubbles


class SimuC(SimuVolumesInt):
    """
    Creation: `rate_prod` bubbles per iteration.

    Bursting: remove bubbles older than `lifetime`.
    """
    __name__ = 'SimuC'
    _params_default = {
            'lifetime': 1,
            'merging_probability': 1,
            }

    _bubble_init = {
            'lifetime': 0,
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
                np.r_[[b.lifetime for b in bubbles]] > self.params['lifetime'])
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
