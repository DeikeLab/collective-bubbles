Code organization
=================

.. _label-modules:

Modules
-------

Base classes, which define advancing scheme and how data is handle and dumped, are coded in `classes`_.
On every iteration, the simulation class ``BaseSimu`` calls successively the 4 following steps, in this order:

1. ``_create_bubbles``,
2. ``_pop_bubbles``,
3. ``_move_bubbles``,
4. ``_merge_bubbles``,

defined as methods of the simulation inherited class, and customizable as desired.
Pre-existing functions can be picked from the corresponding modules (`create`_, `pop`_, `move`_, `merge`_).

The module `main`_ (name may change) is where the different, customized classes are defined.

Classes
-------

Bubble
^^^^^^

Bubbles in the simulation are a list of instances of the class ``classes.Bubble``.
Their attributes (and values) depend on the exact simulation.
The list is modified modified by the different functions listed :ref:`above <label-modules>`, given as argument **and** return.

Simus: parents
^^^^^^^^^^^^^^

So far, bubbles in the simulation can be handled/dumped in the following ways:

``SimuVolumeInt``
    bubbles have integer volumes :math:`V_k = k V_1`, and their counts :math:`n_k` are dumped in the course of the simulation.

``SimuDiameterHist``
    **(under development)** bubbles sizes can take any positive value, and histograms (with pre-defined bins) are dumped at every iteration.

Simus: custom
^^^^^^^^^^^^^
See :ref:`label-classes`.


.. _classes: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/classes.py

.. _create: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/methods_create.py

.. _merge: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/methods_merge.py

.. _pop: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/methods_pop.py

.. _move: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/methods_move.py

.. _main: https://github.com/DeikeLab/collective-bubbles/blob/master/cobubbles/main.py
