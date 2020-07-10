#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
"""
Created on Wed Jun 17 16:56:40 2020

@author: baptiste

Description:
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance

from .classes import Bubble, _create_axis

def merge_bubbles_pair(bubble1, bubble2):
    """
    Pair coalescence definition.

    Parameters
    ----------
    bubble1, bubble2: Bubble instances
        Bubbles to be merged.

    Returns
    -------
    bubble : Bubble instance
        Merged bubble.
    """
    b1, b2 = bubble1, bubble2
    # get intersection of bubbles attributes
    attrs = b1.__dict__.keys() & b1.__dict__.keys()
    kw = {}
    # define merging rules, here volume adds up
    if 'volume' in attrs:
        # multiple rules for the same result
        V1, V2 = b1.volume, b2.volume
        kw['volume'] = V1 + V2
    if 'diameter' in attrs:
        V1, V2 = b1.diameter**3, b2.diameter**3
        kw['diameter'] = (V1 + V2)**(1/3)
    if 'xy' in attrs:
        # bubble location
        xy1, xy2 = np.array(b1.xy), np.array(b2.xy)
        kw['xy'] = (V1*xy1 + V2*xy2)/(V1 + V2)
    # new params
    kw['lifetime'] = 0
    # create new bubble
    bubble = Bubble(**kw)
    return bubble


def merge_bubbles_closest(bubbles, max_dist, 
        show=False, return_locs=False, proba=1):
    """
    Stencil for merging bubbles, closest first, not recursively.

    Parameters
    ----------
    volumes : list
        List of bubbles volumes, length N.

    locs : np.array, shape (N, 2)
        Bubbles location, as a list-like of `x, y` coordinates.

    max_dist : float
        Maximal/threshold distance, below which bubbles merge.

    unit_volume : float, optional
        Unit volume, to compute diameters as `(volumes/unit_volume)**(1/3)`.

    proba : float, optional
        Individual merging probability: 0 for no coalescence, 1 for systematic
        merging.

    Returns
    -------
    sizes : list
        Updated list of bubbles size, length M.

    Notes
    -----
    - Modify and return `sizes` in place.
    - The algorithm is not recursive: if after merging 2 bubbles could be
    merging again, they do not.
    """
    bubbles_old = bubbles.copy()
    # Get bubbles diameter and location
    d = np.r_[[b.diameter for b in bubbles]]
    xy = [b.xy for b in bubbles]
    # Get indices and compute inter-bubble distances
    I, J = np.triu_indices(len(d), k=1)
    D = distance.pdist(xy) - (d[I]+d[J])/2
    # init, sort by decreasing distance (and work with list bottom)
    k_sort = list(np.argsort(D))[::-1]
    merged = []
    # condition: there are (at least) 2 bubbles eligible for merging
    condition = (len(k_sort) > 0) and (D[k_sort[-1]] < max_dist)
    while condition:
        # get shortest distance and indices
        k = k_sort.pop()
        i, j = int(I[k]), int(J[k])
        # prepare condition for next couple of bubbles
        condition = (len(k_sort) > 0) and (D[k_sort[-1]] < max_dist)
        if (i in merged) or (j in merged) or not np.random.binomial(1, proba):
            # if one of the bubbles has merged, jump to next in line
            continue
        # shift i, j indices (compensate for pop rearrange)
        i_sh = len(np.where(np.array(merged) < i)[0])
        j_sh = len(np.where(np.array(merged) < j)[0])
        # get bubbles vol, fill in the `merged` list, compute new bubble vol
        b1 = bubbles.pop(max((i-i_sh, j-j_sh)))
        b2 = bubbles.pop(min((i-i_sh, j-j_sh)))
        b = merge_bubbles_pair(b1, b2)
        bubbles.append(b)
        merged.extend([i, j])
    # display results
    if show != False:
        fig, ax = _create_axis(show)
        for b in bubbles_old:
            cir = plt.Circle(b.xy, b.diameter/2, fc='k', alpha=.4)
            ax.add_patch(cir)
        for b in bubbles:
            cir = plt.Circle(b.xy, b.diameter/2, ec='C3', fc='none')
            ax.add_patch(cir)
        bb = np.r_[[np.array(p.get_extents().inverse_transformed(ax.transAxes))\
                for p in ax.patches]]
        m, M = bb.min(axis=0), bb.max(axis=0)
        ax.set_xlim(m[0, 0], M[1, 0])
        ax.set_ylim(m[0, 1], M[1, 1])
        ax.set_aspect('equal')
    out = bubbles
    if return_locs == True:
        out = volumes, locs_new
    return out

def merge_bubbles_closest_recursive(sizes, distances):
    return sizes

def merge_bubbles_random(sizes, distances):
    return sizes

