# Project Cleanup Report

Cleanup date: 2026-06-24

## Summary

The project was organized into active source files, experiment variants,
benchmark data, documentation, archived legacy notes, and canonical result
folders. No source algorithm behavior was intentionally changed during cleanup.

## Moved Files

| Original path | New path | Reason |
| --- | --- | --- |
| `problems.txt` | `docs/permutation_representation_notes.txt` | Move design note into documentation folder. |
| `results.txt` | `docs/legacy_full_benchmark_run_log.txt` | Move old benchmark console log into documentation folder. |
| `path.txt` | `archive/legacy_project_files/path.txt` | Archive obsolete local navigation scratch note. |
| `docs/positional_problem.tst` | `docs/positional_problem.txt` | Normalize documentation filename extension. |

## Result Files Reorganized

| Original path | New path | Reason |
| --- | --- | --- |
| `results/baseline_parameters_v1_berlin52_runs.csv` | `results/berlin52/baseline/baseline_parameters_v1/runs.csv` | Baseline run CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_berlin52_summary.csv` | `results/berlin52/baseline/baseline_parameters_v1/summary.csv` | Baseline summary CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_dj38_runs.csv` | `results/dj38/baseline/baseline_parameters_v1/runs.csv` | Baseline run CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_dj38_summary.csv` | `results/dj38/baseline/baseline_parameters_v1/summary.csv` | Baseline summary CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_grid_9_runs.csv` | `results/grid_9/baseline/baseline_parameters_v1/runs.csv` | Baseline run CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_grid_9_summary.csv` | `results/grid_9/baseline/baseline_parameters_v1/summary.csv` | Baseline summary CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_qa194_runs.csv` | `results/qa194/baseline/baseline_parameters_v1/runs.csv` | Baseline run CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_qa194_summary.csv` | `results/qa194/baseline/baseline_parameters_v1/summary.csv` | Baseline summary CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_rectangle_6_runs.csv` | `results/rectangle_6/baseline/baseline_parameters_v1/runs.csv` | Baseline run CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_rectangle_6_summary.csv` | `results/rectangle_6/baseline/baseline_parameters_v1/summary.csv` | Baseline summary CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_square_4_runs.csv` | `results/square_4/baseline/baseline_parameters_v1/runs.csv` | Baseline run CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_square_4_summary.csv` | `results/square_4/baseline/baseline_parameters_v1/summary.csv` | Baseline summary CSV moved into canonical benchmark/version/experiment folder. |
| `results/baseline_parameters_v1_wi29_runs.csv` | `results/wi29/v1/baseline_parameters_v1/runs_previous.csv` | Preserved older loose wi29 v1 run CSV with content different from canonical v1 run CSV. |
| `results/baseline_parameters_v1_wi29_summary.csv` | `results/wi29/v1/baseline_parameters_v1/summary_previous.csv` | Preserved older loose wi29 v1 summary CSV with content different from canonical v1 summary CSV. |
| `results/wi29/v1/baseline_parameters_v1_runs.csv` | `results/wi29/v1/baseline_parameters_v1/runs.csv` | V1 wi29 run CSV moved into canonical experiment folder. |
| `results/wi29/v1/baseline_parameters_v1_summary.csv` | `results/wi29/v1/baseline_parameters_v1/summary.csv` | V1 wi29 summary CSV moved into canonical experiment folder. |
| `results/wi29/v2/baseline_parameters_v1_runs.csv` | `results/wi29/v2/baseline_parameters_v1/runs.csv` | V2 wi29 run CSV moved into canonical experiment folder. |
| `results/wi29/v2/baseline_parameters_v1_summary.csv` | `results/wi29/v2/baseline_parameters_v1/summary.csv` | V2 wi29 summary CSV moved into canonical experiment folder. |
| `results/wi29/v3/baseline_parameters_v1_runs.csv` | `results/wi29/v3/baseline_parameters_v1/runs.csv` | V3 wi29 run CSV moved into canonical experiment folder. |
| `results/wi29/v3/baseline_parameters_v1_summary.csv` | `results/wi29/v3/baseline_parameters_v1/summary.csv` | V3 wi29 summary CSV moved into canonical experiment folder. |
| `results/verification_grid9_wi29_grid_9_runs.csv` | `results/grid_9/baseline/verification_grid9_wi29/runs.csv` | Legacy verification run CSV moved into canonical baseline experiment folder. |
| `results/verification_grid9_wi29_grid_9_summary.csv` | `results/grid_9/baseline/verification_grid9_wi29/summary.csv` | Legacy verification summary CSV moved into canonical baseline experiment folder. |
| `results/verification_grid9_wi29_wi29_runs.csv` | `results/wi29/baseline/verification_grid9_wi29/runs.csv` | Legacy verification run CSV moved into canonical baseline experiment folder. |
| `results/verification_grid9_wi29_wi29_summary.csv` | `results/wi29/baseline/verification_grid9_wi29/summary.csv` | Legacy verification summary CSV moved into canonical baseline experiment folder. |
| `results/wi29_parameter_tuning_trials.csv` | `results/wi29/parameter_tuning/current/fixed_budget_discrete_sa_v1/trials.csv` | Corrected parameter-tuning trials moved into canonical current tuning folder. |
| `results/wi29_parameter_tuning_best.csv` | `results/wi29/parameter_tuning/current/fixed_budget_discrete_sa_v1/best.csv` | Corrected parameter-tuning best result moved into canonical current tuning folder. |
| `results/wi29_parameter_tuning_validation_runs.csv` | `results/wi29/parameter_tuning/current/fixed_budget_discrete_sa_v1/validation_runs.csv` | Corrected parameter-tuning validation runs moved into canonical current tuning folder. |
| `results/benchmark_runs_discrete_ana_baseline_v1.csv` | `results/archive/unclassified/benchmark_runs_discrete_ana_baseline_v1.csv` | Older combined benchmark CSV archived because ownership spans multiple instances. |
| `results/benchmark_summary_discrete_ana_baseline_v1.csv` | `results/archive/unclassified/benchmark_summary_discrete_ana_baseline_v1.csv` | Older combined benchmark summary archived because ownership spans multiple instances. |
| `results/grid_9_results.csv` | `results/grid_9/archive/unclassified/grid_9_results.csv` | Older grid_9-only result without experiment metadata archived. |
| `results/param_search_results.csv` | `results/wi29/parameter_tuning/legacy/initial_param_script/param_search_results.csv` | Legacy pre-fix parameter-search output moved under legacy tuning results. |

## Removed Generated Files

- `__pycache__/`
- `experiments/__pycache__/`

These were generated Python bytecode cache directories and can be recreated.

## Duplicate Handling

No byte-identical duplicate CSV files were found. Files with similar names but
different content were preserved with descriptive names such as
`runs_previous.csv` and `summary_previous.csv`.

## Archived Files

- `archive/legacy_project_files/path.txt`
- `results/archive/unclassified/benchmark_runs_discrete_ana_baseline_v1.csv`
- `results/archive/unclassified/benchmark_summary_discrete_ana_baseline_v1.csv`
- `results/grid_9/archive/unclassified/grid_9_results.csv`
- `results/wi29/parameter_tuning/legacy/initial_param_script/param_search_results.csv`

## Unresolved Files

None. All active source, data, documentation, and result files were classified.

## Notes

The request contained conflicting guidance about the final `ANA_EXPERIMENT`
value. The current working selector value was preserved as `v3`.
