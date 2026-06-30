import csv
import os

from benchmarks import run_selected_benchmarks


BENCHMARK_NAME = "wi29"
ANA_EXPERIMENT = "v10"


BENCHMARK_MENU = {
    "square_4": False,
    "rectangle_6": False,
    "grid_9": False,
    "wi29": True,
    "dj38": False,
    "berlin52": False,
}


BASE_PARAMETERS = {
    "number_of_runs": 10,
    "population_size": 30,
    "max_iterations": 6666,
    "rho": 0.20,
    "temperature_start": 0.03,
    "temperature_min": 0.0001,
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
    "case_a_memory_escape_moves": 2,
    "case_a_safe_memory_moves": 1,
    "case_a_memory_top_k_edges": 20,
    "case_a_suspicious_top_k": 5,
    "case_a_suspicious_moves": 1,
    "case_a_stagnation_level_1": 500,
    "case_a_stagnation_level_2": 1500,
    "case_a_double_bridge_min_segment_size": 2,
}


EXPERIMENTS = [
    ("v10-case-a-v9-control", "v9_inversion"),
    ("v10-case-a-memory-complement", "memory_complement"),
    ("v10-case-a-suspicious-edge", "suspicious_edge_replacement"),
    ("v10-case-a-adaptive-memory", "adaptive_memory_escape"),
    ("v10-case-a-adaptive-safe", "adaptive_memory_escape_safe"),
    ("v10-case-a-double-bridge", "double_bridge_escape"),
    ("v10-case-a-ga-lite", "ga_edge_recombination_lite"),
]


SAFE_COMPARISON_EXPERIMENTS = [
    ("v10-case-a-v9-control", "v9_inversion"),
    ("v10-case-a-adaptive-memory", "adaptive_memory_escape"),
    ("v10-case-a-adaptive-safe", "adaptive_memory_escape_safe"),
]


SUMMARY_FIELDS = [
    "experiment_name",
    "case_a_mode",
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
    "notes",
]


def result_summary_path(experiment_name):
    return os.path.join(
        "results",
        BENCHMARK_NAME,
        ANA_EXPERIMENT,
        experiment_name,
        "summary.csv",
    )


def result_runs_path(experiment_name):
    return os.path.join(
        "results",
        BENCHMARK_NAME,
        ANA_EXPERIMENT,
        experiment_name,
        "runs.csv",
    )


def load_summary_row(experiment_name, case_a_mode):
    path = result_summary_path(experiment_name)
    with open(path, newline="") as summary_file:
        summary = next(csv.DictReader(summary_file))

    notes = ""
    if int(float(summary.get("case_a_operator_invalid_routes", 0))) > 0:
        notes = "invalid case-a routes fell back"

    return {
        "experiment_name": experiment_name,
        "case_a_mode": case_a_mode,
        "best_fitness": summary["best_fitness"],
        "average_fitness": summary["mean_fitness"],
        "median_fitness": summary["median_fitness"],
        "worst_fitness": summary["worst_fitness"],
        "average_gap_percent": summary["mean_gap_percent"],
        "success_count": summary["success_count"],
        "success_percentage": summary["success_percentage"],
        "average_runtime_seconds": summary["mean_runtime_seconds"],
        "case_a_operator_calls": summary.get("case_a_operator_calls", 0),
        "case_a_operator_successes": summary.get("case_a_operator_successes", 0),
        "case_a_operator_fallbacks": summary.get("case_a_operator_fallbacks", 0),
        "notes": notes,
    }


def ranking_key(row):
    return (
        float(row["average_gap_percent"]),
        -int(float(row["success_count"])),
        float(row["worst_fitness"]),
        float(row["median_fitness"]),
        float(row["average_runtime_seconds"]),
    )


def write_csv(file_path, rows):
    with open(file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(file_path, ranked_rows):
    with open(file_path, "w") as report_file:
        report_file.write("# V10 Case A Screening Report\n\n")
        report_file.write("Ranked by average gap, success count, worst fitness, ")
        report_file.write("median fitness, then runtime.\n\n")
        report_file.write(
            "| Rank | Experiment | Mode | Avg fitness | Worst | "
            "Success | Avg runtime |\n"
        )
        report_file.write(
            "|---:|---|---|---:|---:|---:|---:|\n"
        )
        for index, row in enumerate(ranked_rows, start=1):
            report_file.write(
                "| "
                + str(index)
                + " | "
                + row["experiment_name"]
                + " | "
                + row["case_a_mode"]
                + " | "
                + row["average_fitness"]
                + " | "
                + row["worst_fitness"]
                + " | "
                + row["success_count"]
                + " | "
                + row["average_runtime_seconds"]
                + " |\n"
            )


def load_seed_fitnesses(experiment_name):
    rows = {}
    with open(result_runs_path(experiment_name), newline="") as runs_file:
        for row in csv.DictReader(runs_file):
            rows[int(row["seed"])] = int(float(row["best_fitness"]))
    return rows


def write_safe_comparison(output_directory):
    control = load_seed_fitnesses("v10-case-a-v9-control")
    adaptive = load_seed_fitnesses("v10-case-a-adaptive-memory")
    adaptive_safe = load_seed_fitnesses("v10-case-a-adaptive-safe")
    rows = []

    for seed in range(1, 11):
        control_fitness = control[seed]
        adaptive_fitness = adaptive[seed]
        safe_fitness = adaptive_safe[seed]
        rows.append(
            {
                "seed": seed,
                "control": control_fitness,
                "adaptive": adaptive_fitness,
                "adaptive_delta": adaptive_fitness - control_fitness,
                "adaptive_safe": safe_fitness,
                "adaptive_safe_delta": safe_fitness - control_fitness,
            }
        )

    csv_path = os.path.join(output_directory, "case_a_safe_comparison.csv")
    with open(csv_path, "w", newline="") as csv_file:
        fieldnames = [
            "seed",
            "control",
            "adaptive",
            "adaptive_delta",
            "adaptive_safe",
            "adaptive_safe_delta",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    markdown_path = os.path.join(output_directory, "case_a_safe_comparison.md")
    with open(markdown_path, "w") as report_file:
        report_file.write("# V10 Case A Safe Comparison\n\n")
        report_file.write(
            "| Seed | Control | Adaptive | Adaptive delta | "
            "Adaptive safe | Adaptive safe delta |\n"
        )
        report_file.write("|---:|---:|---:|---:|---:|---:|\n")
        for row in rows:
            report_file.write(
                "| "
                + str(row["seed"])
                + " | "
                + str(row["control"])
                + " | "
                + str(row["adaptive"])
                + " | "
                + str(row["adaptive_delta"])
                + " | "
                + str(row["adaptive_safe"])
                + " | "
                + str(row["adaptive_safe_delta"])
                + " |\n"
            )

    return rows


def main():
    for experiment_name, case_a_mode in EXPERIMENTS:
        if os.path.exists(result_summary_path(experiment_name)):
            print("Skipping existing:", experiment_name)
            continue
        parameters = BASE_PARAMETERS.copy()
        parameters["case_a_mode"] = case_a_mode
        run_selected_benchmarks(
            BENCHMARK_MENU,
            {BENCHMARK_NAME: parameters},
            experiment_name,
            ANA_EXPERIMENT,
        )

    rows = []
    for experiment_name, case_a_mode in EXPERIMENTS:
        rows.append(load_summary_row(experiment_name, case_a_mode))

    ranked_rows = sorted(rows, key=ranking_key)
    output_directory = os.path.join("results", BENCHMARK_NAME, ANA_EXPERIMENT)
    os.makedirs(output_directory, exist_ok=True)
    write_csv(
        os.path.join(output_directory, "case_a_screening_summary.csv"),
        ranked_rows,
    )
    write_report(
        os.path.join(output_directory, "case_a_screening_report.md"),
        ranked_rows,
    )
    write_safe_comparison(output_directory)

    print("Case A screening complete.")
    print("Best mode:", ranked_rows[0]["case_a_mode"])


if __name__ == "__main__":
    main()
