# Benchmark Data

This folder is for official geographic TSP benchmark files.

The points represent real populated locations. Distances use TSPLIB `EUC_2D`,
which means each straight-line edge distance is rounded to the nearest integer.
These are benchmark distances, not live road-driving distances.

Coordinates must never be modified. The known optimum values are stored in
`benchmarks.py`.

Required files:

```text
wi29.tsp
dj38.tsp
berlin52.tsp
qa194.tsp
```

Sources used:

- `wi29.tsp`, `dj38.tsp`, and `qa194.tsp`: Waterloo national TSP files.
- `berlin52.tsp`: TSPLIB95 file from the Rice TSPLIB archive.

`uy734.tsp` is reserved as a future stress benchmark and is not included in the
default benchmark yet.
