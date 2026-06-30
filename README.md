# Discrete ANA for the Traveling Salesman Problem

## Introduction

This project adapts the continuous Ant Nesting Algorithm (ANA) to
permutation-based symmetric Traveling Salesman Problem instances. It studies how
different discrete movement operators affect ANA behavior on TSP routes.

## Project Goals

- Adapt continuous ANA movement to permutation solutions.
- Evaluate the adaptation on educational and TSPLIB instances.
- Diagnose the limitations of positional swap guidance.
- Test segment inversion as an exploration operator.
- Test edge-guided movement based on global-best route edges.
- Test hybridization with 2-opt local search.

## Algorithm Versions

### Baseline

- Uses an ordered positional swap sequence toward the global-best route.
- Uses random-swap exploration.
- Uses Euclidean tour fitness, with TSPLIB-compatible integer-rounded distances
  for configured TSPLIB instances.

### V1 - Inversion Exploration

- Keeps positive positional guidance.
- Replaces random-swap exploration with segment inversion.
- Controls inversion strength with the ANA movement magnitude.

### V2 - Edge-Guided ANA

- Keeps V1 inversion exploration.
- Identifies missing edges from the global-best route during positive movement.
- Uses targeted segment reversals to introduce selected global-best edges.

V2 chooses reversals because they create desired global-best edges. It does not
systematically test all 2-opt neighbors.

### V3 - Edge-Guided ANA with 2-opt

- Keeps V2.
- Applies first-improvement 2-opt local search to new global-best candidates.
- Systematically tests valid segment reversals.
- Accepts strictly improving 2-opt moves.
- Stops when no single 2-opt move improves the route.

```text
V2:
targeted reversal chosen to create a missing global-best edge

V3:
systematic local search chosen by actual Euclidean fitness improvement
```

## Project Structure

```text
discrete-ana-tsp/
|-- main.py
|-- ana_tsp.py
|-- benchmarks.py
|-- parameter_tuning.py
|-- tsp_problems.py
|-- experiments/
|   |-- ana_tsp_v1.py
|   |-- ana_tsp_v2.py
|   `-- ana_tsp_v3.py
|-- data/
|-- docs/
|   |-- references.md
|   `-- references/
|-- results/
`-- archive/
```

- `main.py` is the main control file for selecting the ANA version,
  benchmarks, and parameters.
- `ana_tsp.py` contains the baseline implementation.
- `benchmarks.py` loads benchmark data, dispatches the selected ANA version,
  runs seeds, and writes CSV output.
- `parameter_tuning.py` contains the fixed-budget parameter search for `wi29`.
- `experiments/` contains V1, V2, and V3.
- `data/` contains TSPLIB `.tsp` benchmark files.
- `results/` contains organized experiment outputs.
- `docs/` contains project notes, reports, and references.
- `docs/references.md` summarizes methodological references without linking
  directly to ignored local PDFs.

## Requirements

The project uses only the Python standard library.

## Running an Experiment

`main.py` is the main control file. Select the ANA version with:

```python
ANA_EXPERIMENT = "baseline"
```

Allowed values:

```text
baseline
v1
v2
v3
```

Enable benchmarks in `BENCHMARK_MENU`:

```python
BENCHMARK_MENU = {
    "square_4": False,
    "rectangle_6": False,
    "grid_9": False,
    "wi29": True,
    "dj38": False,
    "berlin52": False,
}
```

All benchmark parameters remain in `main.py`:

- `number_of_runs`
- `population_size`
- `max_iterations`
- `rho`
- `temperature_start`
- `temperature_min`

Run:

```bash
python main.py
```

## Experiment Naming

Each changed parameter configuration should use a new experiment name:

```python
EXPERIMENT_NAME = "new_experiment_name"
```

This prevents accidental result overwriting and supports reproducibility.

## Results

Experiment outputs use this hierarchy:

```text
results/
`-- <benchmark>/
    `-- <ana_version>/
        `-- <experiment_name>/
            |-- runs.csv
            `-- summary.csv
```

- `runs.csv` contains one row per seed.
- `summary.csv` contains aggregate statistics across runs.
- Lower tour fitness is better.
- Lower percentage gap from the known optimum is better.

Parameter-tuning outputs exist under:

```text
results/wi29/parameter_tuning/current/<search_name>/
results/wi29/parameter_tuning/legacy/<search_name>/
```

## Benchmarks

Built-in educational problems exposed by the benchmark runner:

- `square_4`
- `rectangle_6`
- `grid_9`

TSPLIB problems present in `data/`:

- `wi29`
- `dj38`
- `berlin52`

The TSPLIB loader accepts `EUC_2D` instances. For configured TSPLIB benchmarks,
the implementation uses integer-rounded edge distances.

## Reproducibility

Experiments use explicit seeds. Algorithm versions should be compared using the
same seeds, and comparisons should use equivalent evaluation budgets when
possible. For controlled experiments, change one variable at a time and keep
experiment names unique.

## Current Research Direction

This is an experimental research implementation. It investigates whether
TSP-aware edge-guided movement and 2-opt local search improve the original
positional ANA adaptation. It is not presented as a production-ready or
state-of-the-art TSP solver.

## References

The project was informed by the original ANA paper, a general metaheuristics
reference, and work on permutation-based combinatorial optimization.

[References and methodological foundations](docs/references.md)
