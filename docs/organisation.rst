=================
Code Organization
=================

.. _label-modules:

Parent classes
==============

Bubbles and base simulations are defined as ``class`` objects, and coded in the
module `classes`_.

Bubble
------

A bubble is an instance of the very general class ``Bubble``.
Its attributes depend on the needs of the simulation.
They are defined when instantiating the class (i.e. creating the bubble), and
can be returned with the ``to_dict``, ``to_series``, or ``__dict__`` methods.

A non-exhaustive list includes the following attributes:
``age``,
``diameter``,
``volume``,
``xy``,
``lifetime``, etc.

A simulation treats bubbles as a ``list`` of ``Bubble`` instances, which
it modifies inplace.

Parent simulation
-----------------

The parent simulation is the class ``BaseSimu``.
It defines the advancing scheme by calling successively the 4 following steps,
in this order:

1. ``_create_bubbles``,
2. ``_pop_bubbles``,
3. ``_move_bubbles``,
4. ``_merge_bubbles``,

defined as methods in the simulation inherited class. 
They are all customizable as desired, but **must take and return** the list of
bubbles as only arguments (on which they operate).
Pre-existing functions can be picked from the corresponding modules 
(`create`_, `pop`_, `move`_, `merge`_).

The current list of bubbles is saved as a private attribute ``_bubbles``.
After every step, the list of bubbles is formatted thanks to the private
method ``_format_bubbles`` and dumped into the attribute ``bubbles``.
However, ``BaseSimu`` leaves this method unspecified and does **not** define how
the data is handled, dumped and stored (see next).

Data handling classes
---------------------

Currently, two classes inherit from ``MainSimu`` and define how to 
handle, dump and store data (*i.e.* define ``_format_bubbles``):

``SimuVolumesInt``
^^^^^^^^^^^^^^^^^^

The bubble volume is an integer number of a unit volume :math:`V_k = k V_1`.
At each iteration, bubbles are stored as the count of bubbles of rank `k`.


``SimuHist``
^^^^^^^^^^^^

*Under development.*

Bins are given as a simulation attribute/parameter, and counts (per bin) are 
stored at each iteration.

Writing one's own classes
=========================

Writing one's own simulation is straightforward:

1. Choose a way of handling/dumping/storing the data between the existing
   classes (or define another way).
2. Create daughter class and override the create, move, merge and pop methods,
   **with the list** ``bubbles`` **as both only argument and only return.**

.. code-block:: python
   
   from cobubbles.classes import SimuVolumeInt

   class FakeSimu(SimuVolumeInt):
       __name__ = 'aFakeSimu'
       _params_default = {'max_volume': 10}
       def _pop_bubbles(self, bubbles):
           """
           Pop bubbles with volume larger than `max_volume`.
           """
           V = [b.volume for b in bubbles]
           k, = np.where(V > self.params['max_volume'])
           for i in sorted(k, ascending=False):
               bubbles.pop(k)
           return bubbles


See also
--------

The module `main`_ (name may change) pre-defines different, customized classes,
briefly described in :doc:`simulations`.


.. _classes: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/classes.py

.. _create: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/methods_create.py

.. _merge: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/methods_merge.py

.. _pop: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/methods_pop.py

.. _move: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/methods_move.py

.. _main: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/main.py
