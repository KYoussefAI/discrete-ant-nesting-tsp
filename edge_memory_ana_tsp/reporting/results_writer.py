import csv
import os
import statistics


RUN_FIELDNAMES = [
    "experiment",
    "algorithm",
    "benchmark",
    "seed",
    "population_size",
    "max_iterations",
    "rho",
    "temperature_start",
    "temperature_min",
    "best_fitness",
    "known_optimum",
    "gap_percent",
    "success",
    "valid_route",
    "runtime_seconds",
    "accepted_worse",
    "rejected_worse",
    "case_a",
    "case_b",
    "general",
    "two_opt_calls",
    "two_opt_candidate_checks",
    "two_opt_improvements",
    "three_opt_calls",
    "three_opt_edge_triples_checked",
    "three_opt_reconnections_checked",
    "three_opt_improvements",
    "edge_memory_deposits",
    "edge_memory_evaporations",
    "memory_guided_moves",
    "memory_selected_edges",
    "memory_inserted_edges",
    "memory_failed_insertions",
    "memory_near_best_deposits",
    "memory_global_best_deposits",
    "memory_ranked_pool_rebuilds",
    "memory_dirty_rebuilds",
    "case_a_calls",
    "case_a_successes",
    "case_a_fallbacks",
    "case_b_calls",
    "case_b_successes",
    "case_b_fallbacks",
    "total_fitness_evaluations",
    "best_route",
]


SUMMARY_FIELDNAMES = [
    "experiment",
    "algorithm",
    "benchmark",
    "runs",
    "population_size",
    "max_iterations",
    "rho",
    "temperature_start",
    "temperature_min",
    "best_fitness",
    "average_fitness",
    "worst_fitness",
    "best_gap_percent",
    "average_gap_percent",
    "worst_gap_percent",
    "success_count",
    "average_runtime_seconds",
    "runs_csv",
    "summary_csv",
]


def gap_percent(best_fitness, known_optimum):
    return 100.0 * (best_fitness - known_optimum) / known_optimum


def result_paths(benchmark_name, experiment_name):
    clean_name = experiment_name.replace(" ", "_")
    result_directory = os.path.join("results", benchmark_name, clean_name)
    return (
        result_directory,
        os.path.join(result_directory, "runs.csv"),
        os.path.join(result_directory, "summary.csv"),
    )


def protect_from_overwrite(result_directory):
    if os.path.exists(result_directory):
        raise FileExistsError(
            "Result folder already exists: " + result_directory
            + ". Choose a new experiment name."
        )
    os.makedirs(result_directory)


def build_run_row(experiment_name, algorithm_name, benchmark_name, seed,
                  parameters, result, known_optimum, valid_route,
                  runtime_seconds):
    best_fitness = result["best_fitness"]
    gap = gap_percent(best_fitness, known_optimum)
    row = {
        "experiment": experiment_name,
        "algorithm": algorithm_name,
        "benchmark": benchmark_name,
        "seed": seed,
        "population_size": parameters["population_size"],
        "max_iterations": parameters["max_iterations"],
        "rho": parameters["rho"],
        "temperature_start": parameters["temperature_start"],
        "temperature_min": parameters["temperature_min"],
        "best_fitness": best_fitness,
        "known_optimum": known_optimum,
        "gap_percent": gap,
        "success": abs(best_fitness - known_optimum) < 0.000000001,
        "valid_route": valid_route,
        "runtime_seconds": runtime_seconds,
        "best_route": result["best_route"],
    }
    for fieldname in RUN_FIELDNAMES:
        if fieldname in result:
            row[fieldname] = result[fieldname]
    return row


def write_results(benchmark_name, experiment_name, algorithm_name, parameters,
                  run_rows):
    result_directory, runs_csv, summary_csv = result_paths(
        benchmark_name,
        experiment_name,
    )
    write_csv(runs_csv, RUN_FIELDNAMES, run_rows)
    summary = summarize_rows(
        benchmark_name,
        experiment_name,
        algorithm_name,
        parameters,
        run_rows,
        runs_csv,
        summary_csv,
    )
    write_csv(summary_csv, SUMMARY_FIELDNAMES, [summary])
    return summary


def write_csv(file_path, fieldnames, rows):
    with open(file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize_rows(benchmark_name, experiment_name, algorithm_name, parameters,
                   run_rows, runs_csv, summary_csv):
    known_optimum = run_rows[0]["known_optimum"]
    fitnesses = []
    gaps = []
    runtimes = []
    success_count = 0

    for row in run_rows:
        fitnesses.append(row["best_fitness"])
        gaps.append(row["gap_percent"])
        runtimes.append(row["runtime_seconds"])
        if row["success"]:
            success_count = success_count + 1

    return {
        "experiment": experiment_name,
        "algorithm": algorithm_name,
        "benchmark": benchmark_name,
        "runs": parameters["runs"],
        "population_size": parameters["population_size"],
        "max_iterations": parameters["max_iterations"],
        "rho": parameters["rho"],
        "temperature_start": parameters["temperature_start"],
        "temperature_min": parameters["temperature_min"],
        "best_fitness": min(fitnesses),
        "average_fitness": statistics.mean(fitnesses),
        "worst_fitness": max(fitnesses),
        "best_gap_percent": gap_percent(min(fitnesses), known_optimum),
        "average_gap_percent": statistics.mean(gaps),
        "worst_gap_percent": max(gaps),
        "success_count": success_count,
        "average_runtime_seconds": statistics.mean(runtimes),
        "runs_csv": runs_csv,
        "summary_csv": summary_csv,
    }


def print_run_progress(benchmark_name, seed, row):
    print(
        benchmark_name,
        "seed",
        seed,
        "best",
        row["best_fitness"],
        "gap",
        round(row["gap_percent"], 4),
        "runtime",
        round(row["runtime_seconds"], 3),
    )


def print_summary(summary):
    print(
        summary["benchmark"],
        "best",
        summary["best_fitness"],
        "avg",
        round(summary["average_fitness"], 6),
        "successes",
        str(summary["success_count"]) + "/" + str(summary["runs"]),
        "results",
        summary["summary_csv"],
    )
