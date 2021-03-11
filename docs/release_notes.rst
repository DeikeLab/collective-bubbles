Release notes
=============

v0.4
----
* **Deprecate** ``SimuA`` and ``SimuB``, as the Bernoulli trial at every
  iteration was bursting bubbles at too fast rate.
* Deprecation warnings added.
* New ``SimuD`` features the following simulation and bubble attributes:

  * ``lifetime`` is given to the bubble at creation. After that number of
    iterations, it pops (``Bubble`` attribute)
  * ``age`` replaces the previous meaning of lifetime (``Bubble`` attribute)
  * ``dist_lifetime`` the lifetime distribution is given as an input. Prefers
    to be saved in HDF5 file format (``SimuD`` parameter)

* New global attributes and attributes:

  * ``mean_lifetime`` mean bubble lifetime (``Simu`` attribute)
  * ``production_rate`` adimensioned production rate 
    :math:`\tilde_p = p_1\tau/\mathcal{A}` (``Simu`` attribute)
  * ``get_density_coverage`` (``SimuVolumesInt`` method)

v0.3
----
* Improve data storing and parameters exporting:

  * HDF5, parameters are stored as table attributes, starting with ``params``
  * CSV, parameters are stored in a header tagger ``<params>`` to ``</params>``

* Start building documentation (hosted on readthedocs)

v0.2.1
------

* Erase and replace v0.2 (newly added versioning was buggy).
* More efficient data saving (no need to store 230 in ``int64`` structure).
* Implement ``SimuC``, where bubbles burst after a certain constant time.

v0.1
----

* First public release of CoBubbles
* Contains already the data structure and simulations run in 
