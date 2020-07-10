#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
"""
Created on Wed Apr 8 15:56:33 2020

@author: baptiste

Description: Definition of different simulations.
"""

import numpy as np
from scipy import stats
import importlib as imp
from os.path import split, join, splitext

from .. import markov_bubble
imp.reload(markov_bubble)
from . import DATA, DIRS, classes
imp.reload(classes)
from .classes import SimuVolumesInt, Bubble, SimuDiametersHist
from .methods_merge import merge_bubbles_closest

## DEFAULT NUMERICAL SETTINGS & PHYSICAL CONSTANTS
PARAMS_DEFAULT = {
        'steps': 100,   #simu length
        'width': 30,    #box size
        'n_bubbles': 1,    #initial number of bubbles
        'rate_prod_avg': 16,    #bubble production rate, normal distribution
        'rate_prod_std': 4,
        'meniscus': 1,  #meniscii interaction length
        'merging_probability': 1, #Merging probability, for 2 eligible bubbles
        }

BUBBLE_INIT = {
        'diameter': 1,
        'volume': 1,
        'lifetime': 0,
        }


class SimuA(SimuVolumesInt):
    def _create_bubbles(self, d):
        """
        Append `n` bubbles of unit size, where `n` is normally distributed.
        """
        q_prod = [self.params['rate_prod_'+s] for s in ['avg', 'std']]
        n_new = abs(int(round(stats.norm.rvs(*q_prod))))
        d += n_new*[self.unit]
        return d

    def _pop_bubbles(self, d):
        """
        Pop `n` bubbles, randomly (uniform distribution) chosen in the bubbles
        list. `n` is normally distributed.
        Notes
        -----
        Currently implemented: only uniform popping for every sizes.
        """
        q_pop = [self.params['rate_pop_'+s] for s in ['avg', 'std']]
        n_pop = min((len(d),\
                abs(int(round(stats.norm.rvs(*q_pop))))))
        for k in sorted(np.unique(np.random.randint(len(d), size=n_pop)),\
                        reverse=True):
            d.pop(k)
        # TODO: implement Villermaux pop formula
        return d 

    def _move_bubbles(self, d):
        """
        Scatter bubbles uniformly in a square box.
        Notes
        -----
        This initialisation is of a Markov-kind, in the sense that it disregards
        the dynamics and history of the bubbles.
        """
        xy = np.random.rand(len(d), 2)*self.params['width']
        return xy

    def _merge_bubbles(self, d, locs):
        """
        Merge bubbles, closest first.
        """
        # if no bubbles, jump to next iteration
        if len(d) >= 2:
        # scheme: closest merge first
            d = merge_bubbles_closest(d, locs, self.params['meniscus'],
                    unit_volume=1/self.d_unit**3)
        #TODO: below threshold, pick pairs randomly
        #TODO: implement multi-merging in same step
        return d


class SimuB(SimuVolumesInt):
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


class SimuC(SimuDiametersHist):
    def _create_bubbles(self, bubbles):
        """
        Append `n` bubbles of unit size, where `n` is normally distributed.
        """
        q_prod = [self.params['rate_prod_'+s] for s in ['avg', 'std']]
        n_new = abs(int(round(stats.norm.rvs(*q_prod))))
        d_prod = [self.params['size_prod_'+s] for s in ['avg', 'std']]
        d_new = np.random.normal(*d_prod, size=n_new)
        bubbles += [Bubble(diameter=d, **self._bubble_init) for d in d_new]
        return bubbles

    def _pop_bubbles(self, bubbles):
        """
        Pop `n` bubbles, randomly (uniform distribution) chosen in the bubbles
        list. `n` is normally distributed.
        Notes
        -----
        Currently implemented: only uniform popping for every sizes.
        """
        p = stats.weibull_min.cdf([b.lifetime for b in self._bubbles],\
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
