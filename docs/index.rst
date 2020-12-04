.. Collective Bubbles Simulation documentation master file, created by
   sphinx-quickstart on Thu Dec  3 14:44:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CoBubbles
=========
CoBubbles, for Collective Bubbles Simulations, is a modular Python code for
quickly simulating bubbles on a plane (i.e. at the water surface).


Contents
--------

.. toctree::
   :maxdepth: 1

   install
   release_notes
   code_organization
   simulations


Example
-------
A minimal working example is demonstrated in `this notebook <https://nbviewer.jupyter.org/github/DeikeLab/collective-bubbles/blob/master/examples/minimal_example-SimuB.ipynb>`_.

Provided that ``Simu`` is defined properly:

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
Paper submitted.


..
    Indices and tables
    ==================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
