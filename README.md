# Discrete Volume Model

## Code organization
The package `main` (name may change) contains a meta-class `Simu`, which defines generic methods (see its docstring), in particular the `step_advance` scheme. The latter runs in this order the 4 private methods:
- `_create_bubbles`,
- `_pop_bubbles`,
- `_move_bubbles`,
- `_merge_bubbles`,

which you have to define in the daughter class you're writing.
See `Markov(Simu)` (name may also change) for an example.

## Minimal working example

The parameters of the simulation are given as a dictionary/keywords arguments `params_simu`.
Import, instantiate the `Simu` object, and display parameters:
```
from scripts.markov_bubble import main
s = main.Markov(**params_simu)
s.params #or s.params_df for a view as a pd.Series
```
Then run the simulation for 100 steps and display a *time* series of bubbles number and mean size (figure output may be different):
```
s.run(100)
s.plot_time_series()
```
![Series](examples/time_series1.png)
