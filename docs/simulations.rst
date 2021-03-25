.. _label-classes:

Simulations
===========

The following simulations are already built-in.

``SimuA``
---------

- Steady bubbles production
- Constant rate of bursting, indifferent to bubbles age, size
- Merging based on distance

``SimuB``
---------
**DEPRECATED**

* Steady bubbles production
* Bursting based on bubble age *(badly implemented)*
* Merging based on distance

``SimuC``
---------
* Steady bubbles production
* Bursting based on bubble age: input bubble ``lifetime``, after which it bursts
* Merging based on distance

``SimuD``
---------
*Replace B*

* Steady bubbles production
* Bursting based on bubble age: input lifetime distribution ``dist_lifetime``
  as a ``scipy.stats`` distribution
* Merging based on distance

