# References and Methodological Foundations

This page summarizes the methodological sources used to frame the project. It
does not link directly to local PDF files because reference PDFs are ignored by
Git unless redistribution permission is available.

## Original Ant Nesting Algorithm

The local ANA reference PDF is stored as:

```text
docs/references/ANA_Ant_Nesting_Algorithm_for_Optimizing_Real-Worl.pdf
```

The filename and visible metadata identify it as a local PDF about the Ant
Nesting Algorithm for optimizing real-world problems. The available local tools
could not verify the full author list, venue, year, DOI, or page numbers from
the PDF, so those details are not asserted here.

This source supplies the original continuous ANA formulation, including the
movement equations, Case A, Case B, the general case, `tau`, `rho`, the
global-best solution concept, and the biological inspiration. This repository
adapts ANA to permutation solutions and does not reproduce the continuous method
unchanged.

## Metaheuristics: From Design to Implementation

Verified citation supplied for this project:

El-Ghazali Talbi, *Metaheuristics: From Design to Implementation*, Wiley, 2009.

This reference informed the project's understanding of representation,
neighborhood design, objective functions, simulated annealing, local search,
population-based metaheuristics, hybrid metaheuristics, experimental design,
solution-quality measurement, robustness, statistical comparison, TSP
neighborhoods, and 2-opt.

No local Talbi PDF was present in `docs/references/` during this documentation
update.

## Differential Evolution: A Handbook for Global Permutation-Based Combinatorial Optimization

Verified citation supplied for this project:

Godfrey C. Onwubolu and Donald Davendra, editors, *Differential Evolution: A
Handbook for Global Permutation-Based Combinatorial Optimization*, Springer,
2009.

This reference informed the project's treatment of adapting continuous
operators to permutation problems, why ordinary vector arithmetic is not
naturally meaningful for symbolic permutations, the need for meaningful
permutation representations, property-based movement, and the difference between
arbitrary positional encoding and problem-aware structure.

The book is not cited as proposing this ANA adaptation. No local Onwubolu and
Davendra PDF was present in `docs/references/` during this documentation
update.

## TSPLIB

TSPLIB instances are present in `data/`:

- `wi29`
- `dj38`
- `berlin52`
- `qa194`

Known optimum values are stored in `benchmarks.py` and used for comparison.
The loader accepts `EUC_2D` files, and configured TSPLIB benchmarks use
integer-rounded distances.

A formal TSPLIB bibliographic citation was not present in the project
documentation or source files, so it is not asserted here.

## Literature-derived Concepts

The following concepts come from the broader literature and reference material:

- continuous ANA equations and cases;
- permutation representations;
- neighborhood search;
- simulated annealing;
- segment inversion;
- 2-opt local search;
- experimental comparison principles.

## Project-specific Adaptations

The following are project-specific experimental decisions:

- representing ANA route differences with ordered positional swap sequences;
- using swap count to control partial movement;
- diagnosing that positional proximity does not always produce lower Euclidean
  TSP fitness;
- replacing random-swap exploration with segment inversion in V1;
- introducing missing global-best edge guidance in V2;
- applying first-improvement 2-opt local search in V3;
- using equal or approximately equal evaluation budgets during comparison.

These adaptations should not be read as designs or endorsements from the
reference authors.

## Bibliography

- Talbi, E.-G. (2009). *Metaheuristics: From Design to Implementation*. Wiley.
- Onwubolu, G. C., & Davendra, D. (Eds.). (2009). *Differential Evolution: A Handbook for Global Permutation-Based Combinatorial Optimization*. Springer.
- Original ANA paper. Local PDF: `docs/references/ANA_Ant_Nesting_Algorithm_for_Optimizing_Real-Worl.pdf`. Full bibliographic details could not be verified from the local PDF with the available extraction tools.
