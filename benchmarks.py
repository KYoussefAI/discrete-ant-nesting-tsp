import csv
import os
import statistics
import time

from ana_tsp import is_valid_route
from ana_tsp import run_ana
from tsp_problems import PROBLEMS


BENCHMARKS = {
    "square_4": {
        "source": "built_in",
        "known_optimum": 4.0,
        "use_integer_distances": False,
    },

    "rectangle_6": {
        "source": "built_in",
        "known_optimum": 10.0,
        "use_integer_distances": False,
    },

    "grid_9": {
        "source": "built_in",
        "known_optimum": 9.414213562373095,
        "use_integer_distances": False,
    },

    "wi29": {
        "source": "tsplib",
        "file": "data/wi29.tsp",
        "number_of_cities": 29,
        "known_optimum": 27603,
        "use_integer_distances": True,
    },

    "dj38": {
        "source": "tsplib",
        "file": "data/dj38.tsp",
        "number_of_cities": 38,
        "known_optimum": 6656,
        "use_integer_distances": True,
    },

    "berlin52": {
        "source": "tsplib",
        "file": "data/berlin52.tsp",
        "number_of_cities": 52,
        "known_optimum": 7542,
        "use_integer_distances": True,
    },

    "qa194": {
        "source": "tsplib",
        "file": "data/qa194.tsp",
        "number_of_cities": 194,
        "known_optimum": 9352,
        "use_integer_distances": True,
    },
}


def load_ana_algorithm(ana_experiment):
    if ana_experiment == "baseline":
        return {
            "run_ana": run_ana,
            "is_valid_route": is_valid_route,
        }

    print("Unknown ANA experiment:", ana_experiment)
    print('Allowed values are "baseline".')
    return None


def read_header_value(line):
    if ":" not in line:
        return ""
    parts = line.split(":", 1)
    return parts[1].strip()


def load_tsplib_coordinates(file_path):
    if not os.path.exists(file_path):
        print("Missing file:", file_path)
        return None

    dimension = None
    edge_weight_type = ""
    coordinates = []
    reading_coordinates = False

    with open(file_path, "r") as tsp_file:
        for line in tsp_file:
            line = line.strip()

            if line == "":
                continue

            if line == "EOF":
                break

            if reading_coordinates:
                parts = line.split()
                if len(parts) >= 3:
                    node_id = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    coordinates.append((node_id, x, y))
                continue

            if line.startswith("TYPE"):
                problem_type = read_header_value(line)
                if problem_type != "TSP":
                    print("Unsupported TYPE in", file_path)
                    return None
            elif line.startswith("DIMENSION"):
                dimension = int(read_header_value(line))
            elif line.startswith("EDGE_WEIGHT_TYPE"):
                edge_weight_type = read_header_value(line)
            elif line == "NODE_COORD_SECTION":
                reading_coordinates = True

    if edge_weight_type != "EUC_2D":
        print("Unsupported EDGE_WEIGHT_TYPE in", file_path)
        return None

    if dimension is None:
        print("Missing DIMENSION in", file_path)
        return None

    if len(coordinates) != dimension:
        print("Coordinate count does not match DIMENSION in", file_path)
        return None

    coordinates.sort()

    final_coordinates = []
    for item in coordinates:
        final_coordinates.append((item[1], item[2]))

    return final_coordinates


def load_benchmark_coordinates(benchmark_name, benchmark):
    if benchmark["source"] == "built_in":
        return PROBLEMS[benchmark_name]

    coordinates = load_tsplib_coordinates(benchmark["file"])
    if coordinates is None:
        return None

    if len(coordinates) != benchmark["number_of_cities"]:
        print("Unexpected number of cities in", benchmark["file"])
        print("Expected:", benchmark["number_of_cities"])
        print("Found:", len(coordinates))
        return None

    return coordinates


def clean_experiment_name(experiment_name):
    return experiment_name.replace(" ", "_")


def make_result_directory(benchmark_name, ana_experiment):
    result_directory = os.path.join("results", benchmark_name, ana_experiment)
    os.makedirs(result_directory, exist_ok=True)
    return result_directory


def make_experiment_result_paths(benchmark_name, ana_experiment, experiment_name):
    result_directory = os.path.join(
        "results",
        benchmark_name,
        ana_experiment,
        clean_experiment_name(experiment_name),
    )
    runs_file = os.path.join(result_directory, "runs.csv")
    summary_file = os.path.join(result_directory, "summary.csv")
    return result_directory, runs_file, summary_file


def calculate_summary(run_rows):
    fitness_values = []
    gap_values = []
    runtime_values = []
    success_count = 0

    for row in run_rows:
        fitness_values.append(row["best_fitness"])
        gap_values.append(row["gap_percent"])
        runtime_values.append(row["runtime_seconds"])
        if row["success"] == "yes":
            success_count = success_count + 1

    if len(fitness_values) == 1:
        standard_deviation = 0
    else:
        standard_deviation = statistics.stdev(fitness_values)

    summary = {
        "experiment": run_rows[0]["experiment"],
        "ana_experiment": run_rows[0]["ana_experiment"],
        "benchmark": run_rows[0]["benchmark"],
        "number_of_cities": run_rows[0]["number_of_cities"],
        "number_of_runs": len(run_rows),
        "population_size": run_rows[0]["population_size"],
        "max_iterations": run_rows[0]["max_iterations"],
        "rho": run_rows[0]["rho"],
        "temperature_start": run_rows[0]["temperature_start"],
        "temperature_min": run_rows[0]["temperature_min"],
        "best_fitness": min(fitness_values),
        "mean_fitness": statistics.mean(fitness_values),
        "median_fitness": statistics.median(fitness_values),
        "standard_deviation": standard_deviation,
        "worst_fitness": max(fitness_values),
        "best_gap_percent": min(gap_values),
        "mean_gap_percent": statistics.mean(gap_values),
        "worst_gap_percent": max(gap_values),
        "success_count": success_count,
        "success_percentage": 100 * success_count / len(run_rows),
        "mean_runtime_seconds": statistics.mean(runtime_values),
    }

    return summary


def write_csv(file_path, rows, fieldnames):
    with open(file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def print_selected_benchmarks(benchmark_menu):
    print("Selected benchmarks:")
    for benchmark_name in BENCHMARKS:
        if benchmark_menu.get(benchmark_name) == True:
            print("-", benchmark_name)


def print_parameters(benchmark_name, parameters):
    print("Benchmark:", benchmark_name)
    print("Runs:", parameters["number_of_runs"])
    print("Population size:", parameters["population_size"])
    print("Iterations:", parameters["max_iterations"])
    print("Rho:", parameters["rho"])
    print("Temperature start:", parameters["temperature_start"])
    print("Temperature minimum:", parameters["temperature_min"])


def print_summary(summary, runs_file, summary_file):
    print("Best fitness:", summary["best_fitness"])
    print("Average fitness:", summary["mean_fitness"])
    print("Worst fitness:", summary["worst_fitness"])
    print("Best gap:", summary["best_gap_percent"])
    print("Average gap:", summary["mean_gap_percent"])
    print("Success count:", summary["success_count"])
    print("Success percentage:", summary["success_percentage"])
    print("Average runtime:", summary["mean_runtime_seconds"])
    print("Runs CSV:", runs_file)
    print("Summary CSV:", summary_file)


def run_one_benchmark(
    benchmark_name,
    benchmark,
    parameters,
    experiment_name,
    ana_experiment,
    ana_algorithm,
):
    coordinates = load_benchmark_coordinates(benchmark_name, benchmark)
    if coordinates is None:
        print("Skipping", benchmark_name)
        return

    number_of_runs = parameters["number_of_runs"]
    population_size = parameters["population_size"]
    max_iterations = parameters["max_iterations"]
    rho = parameters["rho"]
    temperature_start = parameters["temperature_start"]
    temperature_min = parameters["temperature_min"]
    use_integer_distances = benchmark["use_integer_distances"]
    known_optimum = benchmark["known_optimum"]
    number_of_cities = len(coordinates)
    result_directory, runs_file, summary_file = make_experiment_result_paths(
        benchmark_name,
        ana_experiment,
        experiment_name,
    )

    if os.path.exists(runs_file) or os.path.exists(summary_file):
        print("Result files already exist for this experiment.")
        print("Use a new EXPERIMENT_NAME before running again.")
        print("Runs CSV:", runs_file)
        print("Summary CSV:", summary_file)
        return

    run_rows = []

    fixed_seeds = list(range(1, number_of_runs + 1))

    for run_number, seed in enumerate(fixed_seeds, start=1):
        print("Run", run_number, "of", number_of_runs, "with seed", seed, flush=True)
        start_time = time.perf_counter()
        result = ana_algorithm["run_ana"](
            coordinates,
            population_size,
            max_iterations,
            seed,
            rho,
            temperature_start,
            temperature_min,
            use_integer_distances,
        )
        runtime = time.perf_counter() - start_time

        if not ana_algorithm["is_valid_route"](result["best_route"], number_of_cities):
            print("Error: invalid route returned")
            continue

        best_fitness = result["best_fitness"]

        if use_integer_distances:
            if best_fitness != int(best_fitness):
                print("Error: TSPLIB fitness is not an integer")
                continue
            best_fitness = int(best_fitness)

        absolute_gap = best_fitness - known_optimum
        gap_percent = 100 * absolute_gap / known_optimum

        success = "no"
        if abs(best_fitness - known_optimum) < 0.000001:
            success = "yes"

        # One evaluation for each initialized ant, then one trial per ant per iteration.
        function_evaluations = population_size + population_size * max_iterations

        row = {
            "experiment": experiment_name,
            "ana_experiment": ana_experiment,
            "benchmark": benchmark_name,
            "seed": seed,
            "number_of_cities": number_of_cities,
            "population_size": population_size,
            "max_iterations": max_iterations,
            "rho": rho,
            "temperature_start": temperature_start,
            "temperature_min": temperature_min,
            "function_evaluations": function_evaluations,
            "best_fitness": best_fitness,
            "known_optimum": known_optimum,
            "absolute_gap": absolute_gap,
            "gap_percent": gap_percent,
            "success": success,
            "runtime_seconds": runtime,
            "accepted_worse": result["accepted_worse"],
            "rejected_worse": result["rejected_worse"],
            "case_a": result["case_a"],
            "case_b": result["case_b"],
            "general": result["general"],
            "best_route": result["best_route"],
        }
        run_rows.append(row)

    if len(run_rows) == 0:
        print("No completed runs for:", benchmark_name)
        return

    summary = calculate_summary(run_rows)
    os.makedirs(result_directory, exist_ok=True)

    run_fieldnames = [
        "experiment",
        "ana_experiment",
        "benchmark",
        "seed",
        "number_of_cities",
        "population_size",
        "max_iterations",
        "rho",
        "temperature_start",
        "temperature_min",
        "function_evaluations",
        "best_fitness",
        "known_optimum",
        "absolute_gap",
        "gap_percent",
        "success",
        "runtime_seconds",
        "accepted_worse",
        "rejected_worse",
        "case_a",
        "case_b",
        "general",
        "best_route",
    ]

    summary_fieldnames = [
        "experiment",
        "ana_experiment",
        "benchmark",
        "number_of_cities",
        "number_of_runs",
        "population_size",
        "max_iterations",
        "rho",
        "temperature_start",
        "temperature_min",
        "best_fitness",
        "mean_fitness",
        "median_fitness",
        "standard_deviation",
        "worst_fitness",
        "best_gap_percent",
        "mean_gap_percent",
        "worst_gap_percent",
        "success_count",
        "success_percentage",
        "mean_runtime_seconds",
    ]

    write_csv(runs_file, run_rows, run_fieldnames)
    write_csv(summary_file, [summary], summary_fieldnames)
    print_summary(summary, runs_file, summary_file)


def run_selected_benchmarks(
    benchmark_menu,
    benchmark_parameters,
    experiment_name,
    ana_experiment="baseline",
):
    os.makedirs("results", exist_ok=True)

    ana_algorithm = load_ana_algorithm(ana_experiment)
    if ana_algorithm is None:
        return

    print("Experiment:", experiment_name)
    print("ANA experiment:", ana_experiment)
    print_selected_benchmarks(benchmark_menu)

    for benchmark_name in BENCHMARKS:
        if benchmark_menu.get(benchmark_name) == True:
            if benchmark_name not in benchmark_parameters:
                print("Missing parameters for:", benchmark_name)
                continue

            parameters = benchmark_parameters[benchmark_name]
            benchmark = BENCHMARKS[benchmark_name]
            print_parameters(benchmark_name, parameters)
            run_one_benchmark(
                benchmark_name,
                benchmark,
                parameters,
                experiment_name,
                ana_experiment,
                ana_algorithm,
            )
