# Collective Bubbles Statistics
Framework to simulate surface bubbles, and study their statistics as a function of a reduced number of parameters (production rate, mean lifetime, merging efficiency, etc).

## Code organization
### Simulation
Base classes and advancing scheme are coded in [`classes`](cobubbles/classes.py).
On every iteration, the simulation class `BaseSimu` calls successively the 4 following steps, in this order:
1. `_create_bubbles`,
2. `_pop_bubbles`,
3. `_move_bubbles`,
4. `_merge_bubbles`,

defined as methods of the simulation inherited class, and customizable as desired.
Pre-existing functions can be picked from the corresponding modules.

So far, bubbles in the simulation can be handled/dumped in the following ways:
- bubbles have integer volumes $V_k = k V_1$, and their counts $n_k$ are dumped in the course of the simulation (`SimuVolumesInt`);
- **(under development)** bubbles sizes can take any positive value, and histograms (with pre-defined bins) are dumped at every iteration (`SimuDiametersHist`).

The module [`main`](cobubbles/main.py) (name may change) is where the different, customized classes are defined.

### Bubbles
Bubbles in the simulation are instances of the class `classes.Bubble`.
Their attributes (and values) depend on the exact simulation.

## Parameters management
### Simulation parameters
Different simulation classes may use different set of parameters. They are defined as dictionaries in [`main`](cobubbles/main.py) with the following hierarchy (lower item values erasing previous ones):
1. module level, common to all classes (*e.g.* domain size `width`): `main._default_params`.
2. class level, defined as a class attribute: `main.Simu._default_params`.
3. class instanciation level: given as keyword attributes when instantiating the class, they are passed on (erasing previous values if any) to `self.params`, where they are ultimately stored.

Additionally, the class name (including module), the current version of the code and a timestamp are printed at instantiation.

### Bubble initialization
Bubbles initialization is handled by `self._bubble_init`, a dictionary with the values used when bubbles are created.
There is currently no way to modify it when instantiating the class, but it can be modified before running the simulation.
However, the first bubbles of the simulation can be given as a list when instantiating the class: `s = main.Simu(bubbles=[list of bubbles])`.

## Minimal working example
The parameters of the simulation are given as a dictionary/keywords arguments `params`.
Depending on the class definition, some parameters may already be defined and assigned default values (e.g. domain size).
Provided the class `Simu` is defined:
```
from cobubbles.main import Simu
params = dict(lifetime=10)
s = Simu(**params)
s.params #or s.params_df for a view as a pd.Series
```
Then run the simulation for 100 steps and display a ``time'' series of bubbles number and mean size (figure output may be different):
```
s.run(100)
s.plot_time_series()
```

### See also
[An example in a notebook.](examples/minimal_example-SimuB.ipynb)

## Installation
As a regular Python package: clone package locally or download a zipped released version then `pip install .`.  Or `pip install -e .` if one plans to edit their own classes.
