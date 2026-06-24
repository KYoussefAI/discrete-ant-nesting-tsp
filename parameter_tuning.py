import csv
import math
import os
import random
import statistics
import time

from ana_tsp import is_valid_route
from ana_tsp import run_ana
from benchmarks import BENCHMARKS
from benchmarks import load_benchmark_coordinates


TUNING_BENCHMARK = "wi29"
TOTAL_ANT_UPDATES = 200000
PARAMETER_SEARCH_NAME = "fixed_budget_discrete_sa_v1"

SEARCH_SEEDS = [1, 2, 3, 4, 5]
VALIDATION_SEEDS = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

TUNING_RANDOM_SEED = 12345
TUNING_TRIALS = 50
TUNING_TEMPERATURE_START = 5.0
TUNING_TEMPERATURE_MIN = 0.001

POPULATION_VALUES = [10, 20, 30, 40, 50, 75, 100]
RHO_VALUES = [0.02, 0.05, 0.10, 0.15, 0.20]
TEMPERATURE_START_VALUES = [0.003, 0.01, 0.03, 0.10, 0.30]
TEMPERATURE_MIN_VALUES = [0.0001, 0.0003, 0.001, 0.003]

PARAMETER_TUNING_DIRECTORY = os.path.join(
    "results",
    TUNING_BENCHMARK,
    "parameter_tuning",
    "current",
    PARAMETER_SEARCH_NAME,
)
TRIALS_FILE = os.path.join(PARAMETER_TUNING_DIRECTORY, "trials.csv")
BEST_FILE = os.path.join(PARAMETER_TUNING_DIRECTORY, "best.csv")
VALIDATION_FILE = os.path.join(PARAMETER_TUNING_DIRECTORY, "validation_runs.csv")


def make_config(population_size, rho, temperature_start, temperature_min):
    return {
        "population_size": population_size,
        "rho": rho,
        "temperature_start": temperature_start,
        "temperature_min": temperature_min,
    }


def config_key(config):
    return (
        config["population_size"],
        config["rho"],
        config["temperature_start"],
        config["temperature_min"],
    )


def max_iterations_for(config):
    return TOTAL_ANT_UPDATES // config["population_size"]


def is_temperature_valid(config):
    return config["temperature_min"] < config["temperature_start"]


def tuning_temperature(trial_number):
    if TUNING_TRIALS <= 1:
        return TUNING_TEMPERATURE_MIN

    progress = (trial_number - 1) / (TUNING_TRIALS - 1)
    return TUNING_TEMPERATURE_START * (
        TUNING_TEMPERATURE_MIN / TUNING_TEMPERATURE_START
    ) ** progress


def move_one_position(value, values, rng):
    index = values.index(value)
    possible_indexes = []

    if index > 0:
        possible_indexes.append(index - 1)
    if index < len(values) - 1:
        possible_indexes.append(index + 1)

    new_index = rng.choice(possible_indexes)
    return values[new_index]


def neighbor_config(current_config, rng):
    parameters = [
        "population_size",
        "rho",
        "temperature_start",
        "temperature_min",
    ]

    for attempt in range(100):
        changed_parameter = rng.choice(parameters)
        candidate = current_config.copy()

        if changed_parameter == "population_size":
            candidate["population_size"] = move_one_position(
                current_config["population_size"],
                POPULATION_VALUES,
                rng,
            )
        elif changed_parameter == "rho":
            candidate["rho"] = move_one_position(
                current_config["rho"],
                RHO_VALUES,
                rng,
            )
        elif changed_parameter == "temperature_start":
            candidate["temperature_start"] = move_one_position(
                current_config["temperature_start"],
                TEMPERATURE_START_VALUES,
                rng,
            )
        else:
            candidate["temperature_min"] = move_one_position(
                current_config["temperature_min"],
                TEMPERATURE_MIN_VALUES,
                rng,
            )

        if is_temperature_valid(candidate):
            return candidate, changed_parameter

    return current_config.copy(), "none"


def calculate_gap_statistics(fitness_values, known_optimum):
    gap_values = []
    for fitness in fitness_values:
        gap = 100 * (fitness - known_optimum) / known_optimum
        gap_values.append(gap)

    return {
        "best_gap_percent": min(gap_values),
        "mean_gap_percent": statistics.mean(gap_values),
        "worst_gap_percent": max(gap_values),
        "gap_standard_deviation": statistics.stdev(gap_values),
    }


def evaluate_config(config, coordinates, benchmark, cache):
    key = config_key(config)
    if key in cache:
        cached_result = cache[key].copy()
        cached_result["cache_hit"] = "yes"
        cached_result["runtime_seconds"] = 0.0
        return cached_result

    start_time = time.perf_counter()
    max_iterations = max_iterations_for(config)
    fitness_values = []
    invalid = False

    for seed in SEARCH_SEEDS:
        result = run_ana(
            coordinates,
            config["population_size"],
            max_iterations,
            seed,
            config["rho"],
            config["temperature_start"],
            config["temperature_min"],
            benchmark["use_integer_distances"],
        )

        if result is None:
            invalid = True
            break

        if not is_valid_route(result["best_route"], len(coordinates)):
            invalid = True
            break

        best_fitness = result["best_fitness"]
        if benchmark["use_integer_distances"]:
            best_fitness = int(best_fitness)
        fitness_values.append(best_fitness)

    runtime_seconds = time.perf_counter() - start_time

    if invalid:
        summary = {
            "population_size": config["population_size"],
            "max_iterations": max_iterations,
            "rho": config["rho"],
            "temperature_start": config["temperature_start"],
            "temperature_min": config["temperature_min"],
            "total_ant_updates": config["population_size"] * max_iterations,
            "mean_fitness": math.inf,
            "best_gap_percent": math.inf,
            "mean_gap_percent": math.inf,
            "worst_gap_percent": math.inf,
            "gap_standard_deviation": math.inf,
            "score": math.inf,
            "runtime_seconds": runtime_seconds,
            "cache_hit": "no",
        }
    else:
        gap_statistics = calculate_gap_statistics(
            fitness_values,
            benchmark["known_optimum"],
        )
        score = (
            gap_statistics["mean_gap_percent"]
            + 0.25 * gap_statistics["gap_standard_deviation"]
        )

        summary = {
            "population_size": config["population_size"],
            "max_iterations": max_iterations,
            "rho": config["rho"],
            "temperature_start": config["temperature_start"],
            "temperature_min": config["temperature_min"],
            "total_ant_updates": config["population_size"] * max_iterations,
            "mean_fitness": statistics.mean(fitness_values),
            "best_gap_percent": gap_statistics["best_gap_percent"],
            "mean_gap_percent": gap_statistics["mean_gap_percent"],
            "worst_gap_percent": gap_statistics["worst_gap_percent"],
            "gap_standard_deviation": gap_statistics["gap_standard_deviation"],
            "score": score,
            "runtime_seconds": runtime_seconds,
            "cache_hit": "no",
        }

    cache[key] = summary.copy()
    return summary


def accept_candidate(current_score, candidate_score, temperature, rng):
    if candidate_score <= current_score:
        return True

    probability = math.exp(-(candidate_score - current_score) / temperature)
    return rng.random() < probability


def write_csv(file_path, rows, fieldnames):
    with open(file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def tune_parameters():
    os.makedirs("results", exist_ok=True)

    benchmark = BENCHMARKS[TUNING_BENCHMARK]
    coordinates = load_benchmark_coordinates(TUNING_BENCHMARK, benchmark)
    if coordinates is None:
        print("Could not load benchmark:", TUNING_BENCHMARK)
        return None, []

    rng = random.Random(TUNING_RANDOM_SEED)
    cache = {}
    trial_rows = []

    current_config = make_config(20, 0.10, 0.01, 0.001)
    current_result = evaluate_config(current_config, coordinates, benchmark, cache)
    best_config = current_config.copy()
    best_result = current_result.copy()

    initial_row = current_result.copy()
    initial_row["trial_number"] = 0
    initial_row["changed_parameter"] = "initial"
    initial_row["accepted_as_current"] = "yes"
    initial_row["new_global_best"] = "yes"
    initial_row["tuning_temperature"] = ""
    trial_rows.append(initial_row)

    for trial_number in range(1, TUNING_TRIALS + 1):
        candidate_config, changed_parameter = neighbor_config(current_config, rng)
        temperature = tuning_temperature(trial_number)
        candidate_result = evaluate_config(
            candidate_config,
            coordinates,
            benchmark,
            cache,
        )

        accepted = accept_candidate(
            current_result["score"],
            candidate_result["score"],
            temperature,
            rng,
        )

        new_global_best = False
        if candidate_result["score"] < best_result["score"]:
            best_config = candidate_config.copy()
            best_result = candidate_result.copy()
            new_global_best = True

        if accepted:
            current_config = candidate_config.copy()
            current_result = candidate_result.copy()

        row = candidate_result.copy()
        row["trial_number"] = trial_number
        row["changed_parameter"] = changed_parameter
        row["accepted_as_current"] = "yes" if accepted else "no"
        row["new_global_best"] = "yes" if new_global_best else "no"
        row["tuning_temperature"] = temperature
        trial_rows.append(row)

        print(
            "Trial",
            trial_number,
            "score",
            candidate_result["score"],
            "accepted",
            row["accepted_as_current"],
            "best",
            best_result["score"],
            flush=True,
        )

    return best_config, best_result, trial_rows, coordinates, benchmark


def validate_best_config(best_config, coordinates, benchmark):
    rows = []
    max_iterations = max_iterations_for(best_config)

    for seed in VALIDATION_SEEDS:
        start_time = time.perf_counter()
        result = run_ana(
            coordinates,
            best_config["population_size"],
            max_iterations,
            seed,
            best_config["rho"],
            best_config["temperature_start"],
            best_config["temperature_min"],
            benchmark["use_integer_distances"],
        )
        runtime_seconds = time.perf_counter() - start_time

        valid_route = "yes"
        if result is None:
            valid_route = "no"
            best_fitness = math.inf
            gap_percent = math.inf
        elif not is_valid_route(result["best_route"], len(coordinates)):
            valid_route = "no"
            best_fitness = math.inf
            gap_percent = math.inf
        else:
            best_fitness = result["best_fitness"]
            if benchmark["use_integer_distances"]:
                best_fitness = int(best_fitness)
            gap_percent = (
                100
                * (best_fitness - benchmark["known_optimum"])
                / benchmark["known_optimum"]
            )

        rows.append(
            {
                "seed": seed,
                "population_size": best_config["population_size"],
                "max_iterations": max_iterations,
                "rho": best_config["rho"],
                "temperature_start": best_config["temperature_start"],
                "temperature_min": best_config["temperature_min"],
                "total_ant_updates": best_config["population_size"]
                * max_iterations,
                "best_fitness": best_fitness,
                "known_optimum": benchmark["known_optimum"],
                "gap_percent": gap_percent,
                "valid_route": valid_route,
                "runtime_seconds": runtime_seconds,
            }
        )

    return rows


def validation_summary(validation_rows):
    fitness_values = []
    gap_values = []
    valid_count = 0

    for row in validation_rows:
        if row["valid_route"] == "yes":
            fitness_values.append(row["best_fitness"])
            gap_values.append(row["gap_percent"])
            valid_count = valid_count + 1

    if valid_count == 0:
        return {
            "validation_valid_runs": 0,
            "validation_mean_fitness": math.inf,
            "validation_best_gap_percent": math.inf,
            "validation_mean_gap_percent": math.inf,
            "validation_worst_gap_percent": math.inf,
            "validation_gap_standard_deviation": math.inf,
        }

    if valid_count == 1:
        standard_deviation = 0.0
    else:
        standard_deviation = statistics.stdev(gap_values)

    return {
        "validation_valid_runs": valid_count,
        "validation_mean_fitness": statistics.mean(fitness_values),
        "validation_best_gap_percent": min(gap_values),
        "validation_mean_gap_percent": statistics.mean(gap_values),
        "validation_worst_gap_percent": max(gap_values),
        "validation_gap_standard_deviation": standard_deviation,
    }


def main():
    if (
        os.path.exists(TRIALS_FILE)
        or os.path.exists(BEST_FILE)
        or os.path.exists(VALIDATION_FILE)
    ):
        print("Parameter tuning results already exist.")
        print("Use a new PARAMETER_SEARCH_NAME before running again.")
        print("Trials:", TRIALS_FILE)
        print("Best:", BEST_FILE)
        print("Validation:", VALIDATION_FILE)
        return

    tuning_result = tune_parameters()
    if tuning_result[0] is None:
        return

    best_config = tuning_result[0]
    best_result = tuning_result[1]
    trial_rows = tuning_result[2]
    coordinates = tuning_result[3]
    benchmark = tuning_result[4]

    trial_fieldnames = [
        "trial_number",
        "changed_parameter",
        "population_size",
        "max_iterations",
        "rho",
        "temperature_start",
        "temperature_min",
        "total_ant_updates",
        "mean_fitness",
        "best_gap_percent",
        "mean_gap_percent",
        "worst_gap_percent",
        "gap_standard_deviation",
        "score",
        "accepted_as_current",
        "new_global_best",
        "tuning_temperature",
        "runtime_seconds",
        "cache_hit",
    ]
    os.makedirs(PARAMETER_TUNING_DIRECTORY, exist_ok=True)
    write_csv(TRIALS_FILE, trial_rows, trial_fieldnames)

    validation_rows = validate_best_config(best_config, coordinates, benchmark)
    validation_fieldnames = [
        "seed",
        "population_size",
        "max_iterations",
        "rho",
        "temperature_start",
        "temperature_min",
        "total_ant_updates",
        "best_fitness",
        "known_optimum",
        "gap_percent",
        "valid_route",
        "runtime_seconds",
    ]
    write_csv(VALIDATION_FILE, validation_rows, validation_fieldnames)

    best_row = best_result.copy()
    best_row["benchmark"] = TUNING_BENCHMARK
    best_row.update(validation_summary(validation_rows))

    best_fieldnames = [
        "benchmark",
        "population_size",
        "max_iterations",
        "rho",
        "temperature_start",
        "temperature_min",
        "total_ant_updates",
        "mean_fitness",
        "best_gap_percent",
        "mean_gap_percent",
        "worst_gap_percent",
        "gap_standard_deviation",
        "score",
        "validation_valid_runs",
        "validation_mean_fitness",
        "validation_best_gap_percent",
        "validation_mean_gap_percent",
        "validation_worst_gap_percent",
        "validation_gap_standard_deviation",
    ]
    write_csv(BEST_FILE, [best_row], best_fieldnames)

    print("Trials:", TRIALS_FILE)
    print("Best:", BEST_FILE)
    print("Validation:", VALIDATION_FILE)


if __name__ == "__main__":
    main()
