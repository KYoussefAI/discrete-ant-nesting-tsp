# Edge-Memory ANA for the Traveling Salesman Problem

This repository contains a standalone Python implementation of **Edge-Memory
ANA**, a discrete adaptation of the Ant Nesting Algorithm (ANA) for the
Traveling Salesman Problem (TSP).

The original ANA is a continuous swarm-intelligence metaheuristic inspired by
the nest-building behavior of Leptothorax ants. Since the TSP is a discrete
permutation problem, the original continuous movement equation cannot be used
directly. This project keeps the main ANA structure while replacing continuous
position updates with valid TSP operators based on edge memory, segment
inversion, mini-reconstruction, simulated annealing acceptance, and 2-opt/3-opt
local improvement.

## Project Context

This work was developed as a project report implementation:

```text
Adaptation de l'ANA au TSP
Version Edge-Memory ANA
```

Author: **Youssef Khaloufi**  
Supervisor: **Pr. Khalid Jebari**  
Academic year: **2025-2026**

The full report is included in:

```text
RAPPORT_Edge_Memory_ANA_TSP_YOUSSEF_KHALOUFI_AIDS.pdf
```

## Objective

The objective is not to replace specialized TSP solvers. Instead, the project
studies how a continuous metaheuristic can be transformed into a correct,
readable, and functional discrete method for TSP.

The implementation focuses on:

- preserving the main ANA ideas: population, best solution, previous position,
  guided movement, and special stagnation cases;
- representing each solution as a valid TSP tour;
- using edge memory to guide search toward useful city connections;
- adding local improvement to polish new global-best tours;
- producing benchmark CSV files for reproducible evaluation.

## Method Summary

### TSP Representation

A solution is represented as a permutation of cities. City `0` is fixed at the
first position to avoid multiple equivalent representations of the same tour.
After each operator, the tour is normalized and validated.

The objective is to minimize the closed-tour distance:

```text
F(route) = distance(route[0], route[1]) + ... + distance(route[n-1], route[0])
```

### Why ANA Must Be Adapted

In the original ANA, each ant has a continuous position and updates it using a
continuous displacement. For TSP, a solution must remain a valid permutation, so
adding a numeric displacement to a route is not meaningful.

Edge-Memory ANA replaces continuous movement with permutation-safe operators:

- memory-guided edge insertion;
- random segment inversion;
- adaptive escape when an ant is already on the global best tour;
- mini-reconstruction when an ant repeats its previous tour.

### Edge Memory

The algorithm maintains a symmetric edge-memory matrix. Each value stores the
learned usefulness of an undirected edge `(i, j)`.

At each iteration:

- memory evaporates slightly;
- edges from the global-best tour receive a deposit;
- accepted near-best tours may receive a smaller deposit;
- high-memory edges are preferred during positive movement.

This is the central adaptation: in TSP, the quality of a tour depends strongly
on the edges it contains, so learned edge structure is more useful than direct
continuous position movement.

### Movement Rules

The implementation uses three main candidate-generation cases:

| Case | Situation | Discrete behavior |
| --- | --- | --- |
| Standard movement | Ant is neither stuck nor equal to the global best | Positive ANA movement inserts high-memory edges; negative movement applies random segment inversion. |
| Case A | Current tour equals the global-best tour | Adaptive escape using memory-guided insertions, increasing exploration when stagnation grows. |
| Case B | Current tour equals the previous tour | Mini-reconstruction using several high-memory edges, with fallback inversion if needed. |

### Acceptance and Local Search

Candidate tours are accepted when they improve the current ant fitness. Worse
candidates may also be accepted using a simulated annealing probability, which
helps the search escape local optima.

Whenever a new global-best tour is found, it is polished using:

1. strict-improvement 2-opt;
2. genuine 3-opt;
3. another 2-opt pass if 3-opt improves the route.

## Implementation Structure

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

docs/
    ANA_Ant_Nesting_Algorithm_for_Optimizing_Real-Worl.pdf
    Differential evolution_ A handbook for global permutation-based combinatorial optimization.pdf
    Metaheuristics_ From Design to Implementation.pdf

results/
    .gitkeep

tests/
    smoke_test.py

tsp_problems.py
```

Important files:

- `core/algorithm_flow.py`: main Edge-Memory ANA loop, written to read like
  pseudocode.
- `core/operators.py`: edge memory, memory-guided movement, Case A, Case B,
  temperature, ANA candidate generation, and simulated annealing acceptance.
- `core/local_search.py`: strict 2-opt, genuine 3-opt, and global-best polishing.
- `core/tsp_utils.py`: distance matrix construction, route validation, tour
  normalization, edge helpers, segment reversal, and TSPLIB loading.
- `experiments/benchmarks.py`: benchmark definitions and default parameters.
- `experiments/runner.py`: benchmark execution over seeds.
- `reporting/results_writer.py`: CSV writing, gap calculation, summary creation,
  and overwrite protection.

## Benchmarks

The project includes three small synthetic benchmarks and two TSPLIB-style
instances.

| Benchmark | Known optimum | Distance mode |
| --- | ---: | --- |
| `square_4` | `4.0` | Euclidean |
| `rectangle_6` | `10.0` | Euclidean |
| `grid_9` | `9.414213562373095` | Euclidean |
| `wi29` | `27603` | TSPLIB integer-rounded Euclidean |
| `dj38` | `6656` | TSPLIB integer-rounded Euclidean |

Default benchmark parameters are defined in `experiments/benchmarks.py`.

## Results Reported in the Project

The final version reached the known optimum on all retained benchmarks with the
configured parameters.

| Benchmark | Runs | Optimum | Best | Mean | Successes | Average time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `square_4` | 10 | 4.0 | 4.0 | 4.0 | 10/10 | 0.028 s |
| `rectangle_6` | 10 | 10.0 | 10.0 | 10.0 | 10/10 | 0.099 s |
| `grid_9` | 30 | 9.4142 | 9.4142 | 9.4142 | 30/30 | 1.061 s |
| `wi29` | 10 | 27603 | 27603 | 27603 | 10/10 | 37.74 s |
| `dj38` | 10 | 6656 | 6656 | 6656 | 10/10 | 38.96 s |

These results validate the implementation on the selected instances. They should
not be interpreted as evidence that the method is stronger than specialized TSP
solvers.

## Running the Project

The project uses only the Python standard library.

From this directory:

```bash
python main.py
```

The default experiment name is:

```text
edge-memory-ana-final
```

Results are written to:

```text
results/<benchmark>/<experiment_name>/runs.csv
results/<benchmark>/<experiment_name>/summary.csv
```

The runner refuses to overwrite an existing result folder. To rerun the full
benchmark set, change `EXPERIMENT_NAME` in `main.py`.

## Smoke Test

Run a small validation test:

```bash
python tests/smoke_test.py
```

The smoke test runs `square_4` with small settings and checks that the pipeline
executes successfully.

## Limitations and Future Work

This project is a study of adaptation, not a production-grade TSP solver. The
main limitation is scalability: as the number of cities increases, 3-opt becomes
computationally expensive.

Possible future improvements:

- compare formally with ACO, GA, SA, and other classical metaheuristics;
- test more TSPLIB instances;
- study the influence of edge-memory parameters;
- optimize or restrict local search to reduce runtime;
- evaluate larger TSP instances with more rigorous statistical protocols.

## Attribution

The Ant Nesting Algorithm was originally proposed by:

```text
Deeam Najmadeen Hama Rashid,
Tarik A. Rashid,
Seyedali Mirjalili
```

in the paper:

```text
ANA: Ant Nesting Algorithm for Optimizing Real-World Problems
```

This repository adapts that ANA concept to the discrete TSP setting through
edge-memory-guided permutation operators.

## References

Reference documents included in `docs/`:

1. Deeam Najmadeen Hama Rashid, Tarik A. Rashid, and Seyedali Mirjalili. `ANA:
   Ant Nesting Algorithm for Optimizing Real-World Problems`. Mathematics,
   2021, 9(23), 3111. DOI: `10.3390/math9233111`.
   File: `docs/ANA_Ant_Nesting_Algorithm_for_Optimizing_Real-Worl.pdf`.
2. El-Ghazali Talbi. `Metaheuristics: From Design to Implementation`. John
   Wiley & Sons, 2009.
   File: `docs/Metaheuristics_ From Design to Implementation.pdf`.
3. Godfrey C. Onwubolu and Donald Davendra, editors. `Differential Evolution:
   A Handbook for Global Permutation-Based Combinatorial Optimization`.
   Springer, 2009. DOI: `10.1007/978-3-540-92151-6`.
   File: `docs/Differential evolution_ A handbook for global permutation-based combinatorial optimization.pdf`.

Additional references cited in the project report:

4. G. Reinelt. `TSPLIB - A Traveling Salesman Problem Library`. ORSA Journal on
   Computing, 1991.
5. G. A. Croes. `A Method for Solving Traveling-Salesman Problems`. Operations
   Research, 1958.
