# Collective Bubbles Statistics
CoBubbles, for Collective Bubbles Simulations, is a modular Python code for simulating bubbles on a plane (i.e. at the water surface).
It creates a framework to study surface bubbles statistics, as a function of a reduced number of parameters (production rate, mean lifetime, merging efficiency, etc).

## Note before you start
The code is intended to be very modular, to try different parameterizations, models, equations.
Just write your own bubbles merging/popping/creation function(s), and plug it in this general framework.

The documentation is hosted [on ReadTheDocs](https://cobubbles.readthedocs.io).

## Installation
As a regular Python package:
-  `pip install git+https://github.com/DeikeLab/collective-bubbles.git@v0.4.1`, specifying the last available release.
- or clone package locally/download a zipped released version then `pip install .` (option `-e `/`--editable` if you plan to edit your own classes).
