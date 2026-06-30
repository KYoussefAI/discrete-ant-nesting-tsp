import ast
import csv
import os
import statistics
import time

from benchmarks import BENCHMARKS
from benchmarks import load_benchmark_coordinates
from experiments import ana_tsp_v11


ANA_EXPERIMENT = "v11"


BENCHMARK_CONFIGS = {
    "wi29": {
        "number_of_runs": 10,
        "population_size": 30,
        "max_iterations": 6666,
        "rho": 0.20,
        "temperature_start": 0.03,
        "temperature_min": 0.0001,
    },
    "berlin52": {
        "number_of_runs": 10,
        "population_size": 60,
        "max_iterations": 3000,
        "rho": 0.08,
        "temperature_start": 0.06,
        "temperature_min": 0.0005,
    },
}


BASE_PARAMETERS = {
    "edge_memory_initial": 1.0,
    "edge_memory_evaporation_rate": 0.02,
    "edge_memory_max": 10.0,
    "global_best_deposit": 1.0,
    "near_best_deposit": 0.3,
    "near_best_gap": 0.03,
    "memory_max_edge_moves": 3,
    "memory_top_k_edges": 20,
    "memory_candidate_pool_size": 100,
    "use_distance_weighted_memory": True,
    "case_b_memory_moves": 1,
    "case_b_memory_top_k_edges": 20,
    "case_b_similarity_threshold": 0.80,
    "case_b_mini_reconstruction_size": 3,
    "case_a_memory_top_k_edges": 20,
    "case_a_stagnation_level_1": 500,
    "case_a_stagnation_level_2": 1500,
    "case_a_double_bridge_min_segment_size": 2,
}


EXPERIMENTS = [
    ("v11-adaptiveA-caseB-control", "v9_original"),
    ("v11-adaptiveA-caseB-memory-direction", "memory_direction"),
    ("v11-adaptiveA-caseB-anti-similarity", "anti_similarity_memory_direction"),
    ("v11-adaptiveA-caseB-mini-reconstruction", "mini_reconstruction"),
]


RUN_FIELDS = [
    "experiment",
    "benchmark",
    "case_a_mode",
    "case_b_mode",
    "seed",
    "best_fitness",
    "known_optimum",
    "absolute_gap",
    "gap_percent",
    "success",
    "runtime_seconds",
    "valid_route",
    "case_a_operator_calls",
    "case_a_operator_successes",
    "case_a_operator_fallbacks",
    "case_a_operator_invalid_routes",
    "case_b_operator_calls",
    "case_b_operator_successes",
    "case_b_operator_fallbacks",
    "case_b_operator_inserted_edges",
    "case_b_operator_invalid_routes",
    "case_b_memory_direction_calls",
    "case_b_memory_direction_insertions",
    "case_b_memory_direction_fallbacks",
    "case_b_memory_direction_invalid_routes",
    "case_b_anti_similarity_calls",
    "case_b_anti_similarity_high_similarity",
    "case_b_anti_similarity_insertions",
    "case_b_anti_similarity_fallbacks",
    "case_b_anti_similarity_invalid_routes",
    "mean_case_b_similarity_to_global_best",
    "case_b_mini_reconstruction_calls",
    "case_b_mini_reconstruction_insertions",
    "case_b_mini_reconstruction_fallbacks",
    "case_b_mini_reconstruction_invalid_routes",
    "memory_failed_insertions",
    "total_fitness_evaluations",
    "best_route",
]


SUMMARY_FIELDS = [
    "benchmark",
    "experiment_name",
    "case_a_mode",
    "case_b_mode",
    "best_fitness",
    "average_fitness",
    "median_fitness",
    "worst_fitness",
    "average_gap_percent",
    "success_count",
    "success_percentage",
    "average_runtime_seconds",
    "case_a_operator_calls",
    "case_a_operator_successes",
    "case_a_operator_fallbacks",
    "case_b_operator_calls",
    "case_b_operator_successes",
    "case_b_operator_fallbacks",
    "case_b_operator_inserted_edges",
    "case_b_operator_invalid_routes",
    "notes",
]


def clean_fitness(value, use_integer_distances):
    if use_integer_distances:
        return int(value)
    return value


def result_directory(benchmark_name, experiment_name):
    return os.path.join("results", benchmark_name, ANA_EXPERIMENT, experiment_name)


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def validate_best_route(route, expected_fitness, coordinates, benchmark):
    distance_matrix = ana_tsp_v11.build_distance_matrix(
        coordinates,
        benchmark["use_integer_distances"],
    )
    computed = clean_fitness(
        ana_tsp_v11.tour_cost(route, distance_matrix),
        benchmark["use_integer_distances"],
    )
    valid = (
        ana_tsp_v11.is_valid_route(route, len(coordinates))
        and len(route) == len(coordinates)
        and route[0] == 0
        and computed == expected_fitness
    )
    return valid, computed


def run_one_experiment(benchmark_name, experiment_name, case_b_mode):
    benchmark = BENCHMARKS[benchmark_name]
    config = BENCHMARK_CONFIGS[benchmark_name]
    coordinates = load_benchmark_coordinates(benchmark_name, benchmark)
    rows = []
    output_directory = result_directory(benchmark_name, experiment_name)
    os.makedirs(output_directory, exist_ok=True)

    for seed in range(1, config["number_of_runs"] + 1):
        print(
            benchmark_name,
            experiment_name,
            "seed",
            seed,
            "of",
            config["number_of_runs"],
            flush=True,
        )
        start_time = time.perf_counter()
        result = ana_tsp_v11.run_ana(
            coordinates=coordinates,
            population_size=config["population_size"],
            max_iterations=config["max_iterations"],
            seed=seed,
            rho=config["rho"],
            temperature_start=config["temperature_start"],
            temperature_min=config["temperature_min"],
            use_integer_distances=benchmark["use_integer_distances"],
            case_b_mode=case_b_mode,
            **BASE_PARAMETERS,
        )
        runtime_seconds = time.perf_counter() - start_time
        best_fitness = clean_fitness(
            result["best_fitness"],
            benchmark["use_integer_distances"],
        )
        valid_route, computed = validate_best_route(
            result["best_route"],
            best_fitness,
            coordinates,
            benchmark,
        )
        if not valid_route:
            print(
                "Warning: invalid best route",
                benchmark_name,
                experiment_name,
                seed,
                "computed",
                computed,
            )
        absolute_gap = best_fitness - benchmark["known_optimum"]
        gap_percent = 100 * absolute_gap / benchmark["known_optimum"]
        row = {
            "experiment": experiment_name,
            "benchmark": benchmark_name,
            "case_a_mode": result["case_a_mode"],
            "case_b_mode": result["case_b_mode"],
            "seed": seed,
            "best_fitness": best_fitness,
            "known_optimum": benchmark["known_optimum"],
            "absolute_gap": absolute_gap,
            "gap_percent": gap_percent,
            "success": "yes" if absolute_gap == 0 else "no",
            "runtime_seconds": runtime_seconds,
            "valid_route": "yes" if valid_route else "no",
            "case_a_operator_calls": result["case_a_operator_calls"],
            "case_a_operator_successes": result["case_a_operator_successes"],
            "case_a_operator_fallbacks": result["case_a_operator_fallbacks"],
            "case_a_operator_invalid_routes": (
                result["case_a_operator_invalid_routes"]
            ),
            "case_b_operator_calls": result["case_b_operator_calls"],
            "case_b_operator_successes": result["case_b_operator_successes"],
            "case_b_operator_fallbacks": result["case_b_operator_fallbacks"],
            "case_b_operator_inserted_edges": (
                result["case_b_operator_inserted_edges"]
            ),
            "case_b_operator_invalid_routes": (
                result["case_b_operator_invalid_routes"]
            ),
            "case_b_memory_direction_calls": (
                result["case_b_memory_direction_calls"]
            ),
            "case_b_memory_direction_insertions": (
                result["case_b_memory_direction_insertions"]
            ),
            "case_b_memory_direction_fallbacks": (
                result["case_b_memory_direction_fallbacks"]
            ),
            "case_b_memory_direction_invalid_routes": (
                result["case_b_memory_direction_invalid_routes"]
            ),
            "case_b_anti_similarity_calls": (
                result["case_b_anti_similarity_calls"]
            ),
            "case_b_anti_similarity_high_similarity": (
                result["case_b_anti_similarity_high_similarity"]
            ),
            "case_b_anti_similarity_insertions": (
                result["case_b_anti_similarity_insertions"]
            ),
            "case_b_anti_similarity_fallbacks": (
                result["case_b_anti_similarity_fallbacks"]
            ),
            "case_b_anti_similarity_invalid_routes": (
                result["case_b_anti_similarity_invalid_routes"]
            ),
            "mean_case_b_similarity_to_global_best": (
                result["mean_case_b_similarity_to_global_best"]
            ),
            "case_b_mini_reconstruction_calls": (
                result["case_b_mini_reconstruction_calls"]
            ),
            "case_b_mini_reconstruction_insertions": (
                result["case_b_mini_reconstruction_insertions"]
            ),
            "case_b_mini_reconstruction_fallbacks": (
                result["case_b_mini_reconstruction_fallbacks"]
            ),
            "case_b_mini_reconstruction_invalid_routes": (
                result["case_b_mini_reconstruction_invalid_routes"]
            ),
            "memory_failed_insertions": result["memory_failed_insertions"],
            "total_fitness_evaluations": result["total_fitness_evaluations"],
            "best_route": result["best_route"],
        }
        rows.append(row)

    write_csv(os.path.join(output_directory, "runs.csv"), rows, RUN_FIELDS)
    summary = summarize_rows(benchmark_name, experiment_name, case_b_mode, rows)
    write_csv(os.path.join(output_directory, "summary.csv"), [summary], SUMMARY_FIELDS)
    return summary


def summarize_rows(benchmark_name, experiment_name, case_b_mode, rows):
    fitness_values = [row["best_fitness"] for row in rows]
    gap_values = [row["gap_percent"] for row in rows]
    runtime_values = [row["runtime_seconds"] for row in rows]
    success_count = len([row for row in rows if row["success"] == "yes"])
    invalid_routes = sum(row["case_b_operator_invalid_routes"] for row in rows)
    case_a_invalid_routes = sum(
        row["case_a_operator_invalid_routes"] for row in rows
    )
    notes = ""
    note_parts = []
    if case_a_invalid_routes > 0:
        note_parts.append("case_a_operator_invalid_routes=" + str(case_a_invalid_routes))
    if invalid_routes > 0:
        note_parts.append("case_b_operator_invalid_routes=" + str(invalid_routes))
    notes = "; ".join(note_parts)
    return {
        "benchmark": benchmark_name,
        "experiment_name": experiment_name,
        "case_a_mode": "adaptive_memory_escape",
        "case_b_mode": case_b_mode,
        "best_fitness": min(fitness_values),
        "average_fitness": statistics.mean(fitness_values),
        "median_fitness": statistics.median(fitness_values),
        "worst_fitness": max(fitness_values),
        "average_gap_percent": statistics.mean(gap_values),
        "success_count": success_count,
        "success_percentage": 100 * success_count / len(rows),
        "average_runtime_seconds": statistics.mean(runtime_values),
        "case_a_operator_calls": sum(row["case_a_operator_calls"] for row in rows),
        "case_a_operator_successes": sum(
            row["case_a_operator_successes"] for row in rows
        ),
        "case_a_operator_fallbacks": sum(
            row["case_a_operator_fallbacks"] for row in rows
        ),
        "case_b_operator_calls": sum(row["case_b_operator_calls"] for row in rows),
        "case_b_operator_successes": sum(
            row["case_b_operator_successes"] for row in rows
        ),
        "case_b_operator_fallbacks": sum(
            row["case_b_operator_fallbacks"] for row in rows
        ),
        "case_b_operator_inserted_edges": sum(
            row["case_b_operator_inserted_edges"] for row in rows
        ),
        "case_b_operator_invalid_routes": invalid_routes,
        "notes": notes,
    }


def ranking_key(row):
    return (
        float(row["average_gap_percent"]),
        -int(row["success_count"]),
        float(row["worst_fitness"]),
        float(row["median_fitness"]),
        float(row["average_runtime_seconds"]),
    )


def write_report(rows):
    path = os.path.join("results", "v11_case_b_screening_report.md")
    with open(path, "w") as report:
        report.write("# V11 Case B Screening Report\n\n")
        for benchmark_name in BENCHMARK_CONFIGS:
            report.write("## " + benchmark_name + "\n\n")
            benchmark_rows = [
                row for row in rows if row["benchmark"] == benchmark_name
            ]
            benchmark_rows.sort(key=ranking_key)
            report.write(
                "| Rank | Experiment | Case A | Case B | Avg fitness | Worst | "
                "Success | Avg runtime |\n"
            )
            report.write("|---:|---|---|---|---:|---:|---:|---:|\n")
            for index, row in enumerate(benchmark_rows, start=1):
                report.write(
                    "| "
                    + str(index)
                    + " | "
                    + row["experiment_name"]
                    + " | "
                    + row["case_a_mode"]
                    + " | "
                    + row["case_b_mode"]
                    + " | "
                    + str(row["average_fitness"])
                    + " | "
                    + str(row["worst_fitness"])
                    + " | "
                    + str(row["success_count"])
                    + " | "
                    + str(row["average_runtime_seconds"])
                    + " |\n"
                )
            report.write("\n")


def load_run_fitnesses(benchmark_name, experiment_name):
    path = os.path.join(result_directory(benchmark_name, experiment_name), "runs.csv")
    fitnesses = {}
    with open(path, newline="") as runs_file:
        for row in csv.DictReader(runs_file):
            fitnesses[int(row["seed"])] = int(float(row["best_fitness"]))
    return fitnesses


def write_seed_comparison(benchmark_name):
    control = load_run_fitnesses(benchmark_name, "v11-adaptiveA-caseB-control")
    memory = load_run_fitnesses(
        benchmark_name,
        "v11-adaptiveA-caseB-memory-direction",
    )
    anti = load_run_fitnesses(
        benchmark_name,
        "v11-adaptiveA-caseB-anti-similarity",
    )
    mini = load_run_fitnesses(
        benchmark_name,
        "v11-adaptiveA-caseB-mini-reconstruction",
    )
    rows = []
    for seed in range(1, 11):
        rows.append(
            {
                "seed": seed,
                "control": control[seed],
                "memory_direction": memory[seed],
                "memory_delta": memory[seed] - control[seed],
                "anti_similarity": anti[seed],
                "anti_similarity_delta": anti[seed] - control[seed],
                "mini_reconstruction": mini[seed],
                "mini_reconstruction_delta": mini[seed] - control[seed],
            }
        )
    path = os.path.join("results", benchmark_name, ANA_EXPERIMENT)
    os.makedirs(path, exist_ok=True)
    write_csv(
        os.path.join(path, "case_b_seed_comparison.csv"),
        rows,
        [
            "seed",
            "control",
            "memory_direction",
            "memory_delta",
            "anti_similarity",
            "anti_similarity_delta",
            "mini_reconstruction",
            "mini_reconstruction_delta",
        ],
    )
    return rows


def main():
    os.makedirs("results", exist_ok=True)
    summaries = []
    for benchmark_name in BENCHMARK_CONFIGS:
        for experiment_name, case_b_mode in EXPERIMENTS:
            summaries.append(
                run_one_experiment(benchmark_name, experiment_name, case_b_mode)
            )

    write_csv(
        os.path.join("results", "v11_case_b_screening_summary.csv"),
        summaries,
        SUMMARY_FIELDS,
    )
    write_report(summaries)
    for benchmark_name in BENCHMARK_CONFIGS:
        write_seed_comparison(benchmark_name)

    print("V11 Case B screening complete.")


if __name__ == "__main__":
    main()
