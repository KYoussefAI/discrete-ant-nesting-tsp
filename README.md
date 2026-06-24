# Discrete ANA for the Traveling Salesman Problem

This project adapts the continuous Ant Nesting Algorithm (ANA) to
permutation-based symmetric TSP instances.

## Baseline

The baseline implementation in `ana_tsp.py` uses an ordered positional swap
sequence toward the global-best route and random-swap exploration. Fitness is
the Euclidean tour length; configured TSPLIB instances use integer-rounded
`EUC_2D` distances.

## Project Structure

```text
discrete-ana-tsp/
|-- main.py
|-- ana_tsp.py
|-- benchmarks.py
|-- parameter_tuning.py
|-- tsp_problems.py
|-- data/
|-- docs/
`-- results/
```

## Running

Configure benchmarks and parameters in `main.py`, then run:

```bash
python main.py
```

Use a new `EXPERIMENT_NAME` for each changed configuration so result files are
not overwritten.

## Results

Results are organized as:

```text
results/<benchmark>/baseline/<experiment_name>/runs.csv
results/<benchmark>/baseline/<experiment_name>/summary.csv
```

Lower tour fitness and lower percentage gap are better.

See `results/README.md` for the result layout.
