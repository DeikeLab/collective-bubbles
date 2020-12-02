# Collective Bubbles Statistics
Framework to simulate surface bubbles, and study their statistics as a function of a reduced number of parameters (production rate, mean lifetime, merging efficiency, etc).

## Code organization
Base classes and advancing scheme are coded in [`classes`](cobubbles/classes.py).
On every iteration, the simulation class `BaseSimu` calls successively the 4 following steps, in this order:
- `_create_bubbles`,
- `_pop_bubbles`,
- `_move_bubbles`,
- `_merge_bubbles`,
defined as methods of the simulation inherited class, and customizable as desired.
Pre-existing functions can be picked from the corresponding modules.

So far, bubbles in the simulation can be handled/dumped in the following ways:
- bubbles have integer volumes $V_k = k V_1$, and their counts $n_k$ are dumped in the course of the simulation (`SimuVolumesInt`);
- (under development) bubbles sizes can take any positive value, and histograms (with pre-defined bins) are dumped at every iteration (`SimuDiametersHist`).

The module [`main`](cobubbles/main.py) (name may change) is where the different, customized classes are defined.

## Minimal working example
The parameters of the simulation are given as a dictionary/keywords arguments `params_simu`.
Depending on the class definition, some parameters may already be defined and assigned default values (e.g. domain size).
Provided the class `Simu` is defined:
```
from cobubbles.main import Simu
params_simu = dict(lifetime=10)
s = Simu(**params_simu)
s.params #or s.params_df for a view as a pd.Series
```
Then run the simulation for 100 steps and display a *time* series of bubbles number and mean size (figure output may be different):
```
s.run(100)
s.plot_time_series()
```
![Series](examples/time_series1.png)
