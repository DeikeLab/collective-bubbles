.. Collective Bubbles Simulation documentation master file, created by
   sphinx-quickstart on Thu Dec  3 14:44:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CoBubbles
=========
CoBubbles stands for Collective Bubbles Simulations.
It is a modular Python code for simulating bubbles on a plane (for instance,
air bubbles at the surface of water).

Contents
--------

.. toctree::
   :maxdepth: 1

   install
   organisation
   simulations
   release_notes

Example
-------
A minimal working example is demonstrated in `this notebook <https://nbviewer.jupyter.org/github/DeikeLab/collective-bubbles/blob/master/examples/minimal_example-SimuB.ipynb>`_.

Provided that ``Simu`` is defined properly, the following code instantiates a
simulation with the given parameters ``params``:

.. code-block:: python
   
   from cobubbles.main import Simu
   params = dict(lifetime=10)
   s = Simu(**params)
   s.params # or s.params_df for a view as a pd.Series

Then run the simulation for 100 steps and display a *time* series of bubbles number :math:`n` and mean size :math:`\langle d/d_1 \rangle` (figure output may be different for one run to the next):

.. code-block:: python

    s.run(100)
    s.plot_time_series()

References
----------
Néel, B. and Deike, L., *Collective bursting of free surface bubbles, and the
role of surface contamination*, accepted at J. Fluid Mech.

..
    Indices and tables
    ==================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
