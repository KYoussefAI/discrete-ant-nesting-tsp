# Results Layout

Results are organized by benchmark, ANA version, and experiment name:

```text
results/<benchmark>/<ana_experiment>/<experiment_name>/runs.csv
results/<benchmark>/<ana_experiment>/<experiment_name>/summary.csv
```

`runs.csv` contains one row per seed/run, including parameters, best fitness,
gap, runtime, counters, and the best route.

`summary.csv` aggregates the runs for one benchmark/version/experiment,
including best, mean, median, standard deviation, worst fitness, gap summaries,
success counts, runtime, and optional version-specific diagnostics.

ANA versions:

- `baseline`: positional swap-based ANA.
- `v1`: inversion exploration for Case A and negative movement.
- `v2`: edge-guided positive movement using targeted segment reversals.
- `v3`: v2 plus first-improvement 2-opt local search on new global-best
  candidates.

Parameter tuning results live under:

```text
results/wi29/parameter_tuning/current/<search_name>/
results/wi29/parameter_tuning/legacy/<search_name>/
```

`current` is for the corrected fixed-budget discrete parameter tuner.
`legacy` is reserved for older pre-fix tuner outputs.

Lower TSP fitness and lower gap percentage are better.
