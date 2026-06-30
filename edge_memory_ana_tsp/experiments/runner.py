import time

from core.algorithm_flow import ALGORITHM_NAME
from core.algorithm_flow import run_edge_memory_ana_tsp
from core.tsp_utils import is_valid_route
from core.tsp_utils import load_tsplib_coordinates
from experiments.benchmarks import BENCHMARKS
from experiments.benchmarks import DEFAULT_BENCHMARK_PARAMETERS
from reporting.results_writer import build_run_row
from reporting.results_writer import print_run_progress
from reporting.results_writer import print_summary
from reporting.results_writer import protect_from_overwrite
from reporting.results_writer import result_paths
from reporting.results_writer import write_results
from tsp_problems import PROBLEMS


def run_all_default_benchmarks(experiment_name):
    summaries = []
    for benchmark_name in BENCHMARKS:
        summary = run_benchmark(
            benchmark_name,
            DEFAULT_BENCHMARK_PARAMETERS[benchmark_name],
            experiment_name,
        )
        summaries.append(summary)
        print_summary(summary)
        print()
    return summaries


def run_benchmark(benchmark_name, parameters, experiment_name):
    coordinates = load_benchmark_coordinates(benchmark_name)
    benchmark = BENCHMARKS[benchmark_name]
    result_directory = result_paths(benchmark_name, experiment_name)[0]
    protect_from_overwrite(result_directory)

    run_rows = []
    for run_index in range(parameters["runs"]):
        seed = run_index + 1
        run_parameters = parameters.copy()
        del run_parameters["runs"]
        run_parameters["seed"] = seed
        run_parameters["use_integer_distances"] = benchmark["use_integer_distances"]

        started_at = time.time()
        result = run_edge_memory_ana_tsp(coordinates, **run_parameters)
        runtime_seconds = time.time() - started_at

        row = build_run_row(
            experiment_name,
            ALGORITHM_NAME,
            benchmark_name,
            seed,
            parameters,
            result,
            benchmark["known_optimum"],
            is_valid_route(result["best_route"], len(coordinates)),
            runtime_seconds,
        )
        run_rows.append(row)
        print_run_progress(benchmark_name, seed, row)

    return write_results(
        benchmark_name,
        experiment_name,
        ALGORITHM_NAME,
        parameters,
        run_rows,
    )


def load_benchmark_coordinates(benchmark_name):
    if benchmark_name in PROBLEMS:
        return PROBLEMS[benchmark_name]
    return load_tsplib_coordinates(BENCHMARKS[benchmark_name]["file"])
