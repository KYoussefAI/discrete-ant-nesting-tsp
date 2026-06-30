# Edge-Memory ANA for TSP

This is a small standalone Python implementation of the final Edge-Memory
Ant Nesting Algorithm for the Traveling Salesman Problem.

The code is organized so the algorithm flow is easy to study first, while
operators, local search, benchmark running, and CSV reporting live in separate
files.

## Read This First

Start with:

```text
core/algorithm_flow.py
```

That file contains `run_edge_memory_ana_tsp` and the complete high-level search
loop. It is written to read like pseudocode:

- initialize the search
- update edge memory and temperature each iteration
- generate one candidate per ant
- accept or reject with simulated annealing
- deposit near-best memory
- polish new global best routes
- record history
- return the final result

## Project Structure

```text
main.py

core/
    algorithm_flow.py
    operators.py
    local_search.py
    tsp_utils.py

experiments/
    benchmarks.py
    runner.py

reporting/
    results_writer.py

data/
    wi29.tsp
    dj38.tsp

results/
    .gitkeep

tests/
    smoke_test.py
```

`core/algorithm_flow.py` is the main algorithm file. Read this first to
understand the full Edge-Memory ANA flow.

`core/operators.py` contains the ANA operators: edge memory, dirty ranked
memory cache, memory-guided movement, segment inversion, adaptive Case A,
mini-reconstruction Case B, temperature, random ANA values, and simulated
annealing acceptance.

`core/local_search.py` contains only strict-improvement 2-opt, genuine 3-opt,
and the polish routine used when a new global best is found.

`core/tsp_utils.py` contains general TSP helpers: distances, route validation,
tour normalization, edge helpers, segment reversal, random inversion, and
TSPLIB coordinate loading.

`experiments/benchmarks.py` contains only benchmark definitions and default
parameters.

`experiments/runner.py` loads benchmark coordinates, loops over seeds, calls
the algorithm, collects rows, and delegates result writing.

`reporting/results_writer.py` contains CSV fields, gap calculations, summary
building, anti-overwrite protection, and printing.

## Algorithm

The final algorithm uses only these ideas:

- route is a permutation with city `0` fixed at index `0`
- fitness is closed-tour distance
- maintain an undirected edge-memory matrix
- keep a dirty cached ranking of memory edges
- positive movement inserts high-memory missing edges by segment reversal
- negative movement uses random segment inversion
- Case A uses adaptive memory escape when an ant is on the global best
- Case B uses mini reconstruction when an ant repeats its previous route
- worse candidates can be accepted by simulated annealing
- new global-best candidates are polished with strict 2-opt and genuine 3-opt

## Benchmarks

Included benchmarks:

- `square_4`
- `rectangle_6`
- `grid_9`
- `wi29`
- `dj38`

Known optima:

- `square_4`: `4.0`
- `rectangle_6`: `10.0`
- `grid_9`: `9.414213562373095`
- `wi29`: `27603`
- `dj38`: `6656`

`wi29` and `dj38` use TSPLIB integer-rounded Euclidean distances.

## Run

From this folder:

```bash
python main.py
```

Results are written to:

```text
results/<benchmark>/<experiment_name>/runs.csv
results/<benchmark>/<experiment_name>/summary.csv
```

The default experiment name is `edge-memory-ana-final`. The runner refuses to
overwrite existing result folders, so change `EXPERIMENT_NAME` in `main.py`
before rerunning the full benchmark set.

## Smoke Test

```bash
python tests/smoke_test.py
```

The smoke test runs only `square_4` with small settings.
