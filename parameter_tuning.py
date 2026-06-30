import argparse
import csv
import inspect
import math
import os
import random
import statistics
import time

from benchmarks import BENCHMARKS
from benchmarks import available_ana_experiments
from benchmarks import load_ana_algorithm
from benchmarks import load_benchmark_coordinates

# Berlin52 V11 exploration run:
# python parameter_tuning.py

ANA_EXPERIMENT = "v11"
TUNING_BENCHMARK = "berlin52"
TOTAL_ANT_UPDATES = 200000
PARAMETER_SEARCH_NAME = "v11_berlin52_exploration_5seeds"
DEFAULT_TUNE_ONLY = (
    "population_size,max_iterations,rho,temperature_start,near_best_gap,"
    "memory_max_edge_moves,case_b_mini_reconstruction_size"
)

SEARCH_SEEDS = [1, 2, 3, 4, 5]
VALIDATION_SEEDS = [11, 12, 13, 14, 15]

TUNING_RANDOM_SEED = 12345
TUNING_TRIALS = 50
TUNING_TEMPERATURE_START = 5.0
TUNING_TEMPERATURE_MIN = 0.001

POPULATION_VALUES = [60, 80, 100]
MAX_ITERATIONS_VALUES = [3000, 5000, 7000]
RHO_VALUES = [0.08, 0.12, 0.16]
TEMPERATURE_START_VALUES = [0.06, 0.08, 0.10]
TEMPERATURE_MIN_VALUES = [0.0001, 0.0003, 0.001, 0.003]
TWO_OPT_TRIGGER_TEMPERATURE_START_VALUES = [0.003, 0.01, 0.03, 0.10, 0.30]
TWO_OPT_TRIGGER_TEMPERATURE_MIN_VALUES = [0.0001, 0.0003, 0.001, 0.003]
ARCHIVE_SIZE_VALUES = [3, 5, 8, 10]
ARCHIVE_MIN_EDGE_DIVERSITY_VALUES = [0.15, 0.20, 0.25]
ARCHIVE_NEAR_BEST_GAP_VALUES = [0.01, 0.02, 0.03]
TABU_TENURE_VALUES = [5, 7, 10]
TABU_MAX_STEPS_VALUES = [25, 50, 75]
TABU_NO_IMPROVEMENT_LIMIT_VALUES = [10, 20, 30]
TABU_CANDIDATE_SAMPLE_SIZE_VALUES = [None, 100, 250, 500]
ILS_ITERATIONS_VALUES = [0, 3, 5, 8]
DOUBLE_BRIDGE_MIN_SEGMENT_SIZE_VALUES = [2, 3, 4]
EDGE_MEMORY_EVAPORATION_RATE_VALUES = [0.01, 0.02, 0.05, 0.10]
EDGE_MEMORY_MAX_VALUES = [5.0, 10.0, 20.0]
GLOBAL_BEST_DEPOSIT_VALUES = [0.5, 1.0, 2.0]
NEAR_BEST_DEPOSIT_VALUES = [0.1, 0.3, 0.5]
NEAR_BEST_GAP_VALUES = [0.03, 0.05]
MEMORY_MAX_EDGE_MOVES_VALUES = [3, 4]
MEMORY_TOP_K_EDGES_VALUES = [5, 10, 20, 40]
MEMORY_CANDIDATE_POOL_SIZE_VALUES = [50, 100, 200, 400]
USE_DISTANCE_WEIGHTED_MEMORY_VALUES = [True, False]
CASE_A_MODE_VALUES = ["adaptive_memory_escape"]
CASE_B_MODE_VALUES = [
    "v9_original",
    "memory_direction",
    "anti_similarity_memory_direction",
    "mini_reconstruction",
]
CASE_B_MEMORY_MOVES_VALUES = [1, 2, 3]
CASE_B_MEMORY_TOP_K_EDGES_VALUES = [5, 10, 20, 40]
CASE_B_SIMILARITY_THRESHOLD_VALUES = [0.70, 0.80, 0.90]
CASE_B_MINI_RECONSTRUCTION_SIZE_VALUES = [3, 4, 5]
USE_CANDIDATE_LISTS_VALUES = [True, False]
CANDIDATE_LIST_SIZE_VALUES = [5, 10, 15, 20]
CANDIDATE_LIST_APPLY_TO_2OPT_VALUES = [True, False]
CANDIDATE_LIST_APPLY_TO_3OPT_VALUES = [True, False]

PARAMETER_DEFAULTS = {
    "population_size": 60,
    "max_iterations": 5000,
    "rho": 0.12,
    "temperature_start": 0.08,
    "temperature_min": 0.001,
    "two_opt_trigger_temperature_start": 0.01,
    "two_opt_trigger_temperature_min": 0.001,
    "archive_size": 5,
    "archive_min_edge_diversity": 0.25,
    "archive_near_best_gap": 0.05,
    "tabu_tenure": 7,
    "tabu_max_steps": 50,
    "tabu_no_improvement_limit": 20,
    "tabu_candidate_sample_size": None,
    "ils_iterations": 5,
    "double_bridge_min_segment_size": 2,
    "edge_memory_evaporation_rate": 0.02,
    "edge_memory_max": 10.0,
    "global_best_deposit": 1.0,
    "near_best_deposit": 0.3,
    "near_best_gap": 0.03,
    "memory_max_edge_moves": 3,
    "memory_top_k_edges": 20,
    "memory_candidate_pool_size": 100,
    "use_distance_weighted_memory": True,
    "case_a_mode": "adaptive_memory_escape",
    "case_b_mode": "mini_reconstruction",
    "case_b_memory_moves": 1,
    "case_b_memory_top_k_edges": 20,
    "case_b_similarity_threshold": 0.80,
    "case_b_mini_reconstruction_size": 3,
    "use_candidate_lists": True,
    "candidate_list_size": 15,
    "candidate_list_apply_to_2opt": True,
    "candidate_list_apply_to_3opt": True,
}

PARAMETER_VALUES = {
    "population_size": POPULATION_VALUES,
    "max_iterations": MAX_ITERATIONS_VALUES,
    "rho": RHO_VALUES,
    "temperature_start": TEMPERATURE_START_VALUES,
    "temperature_min": TEMPERATURE_MIN_VALUES,
    "two_opt_trigger_temperature_start": TWO_OPT_TRIGGER_TEMPERATURE_START_VALUES,
    "two_opt_trigger_temperature_min": TWO_OPT_TRIGGER_TEMPERATURE_MIN_VALUES,
    "archive_size": ARCHIVE_SIZE_VALUES,
    "archive_min_edge_diversity": ARCHIVE_MIN_EDGE_DIVERSITY_VALUES,
    "archive_near_best_gap": ARCHIVE_NEAR_BEST_GAP_VALUES,
    "tabu_tenure": TABU_TENURE_VALUES,
    "tabu_max_steps": TABU_MAX_STEPS_VALUES,
    "tabu_no_improvement_limit": TABU_NO_IMPROVEMENT_LIMIT_VALUES,
    "tabu_candidate_sample_size": TABU_CANDIDATE_SAMPLE_SIZE_VALUES,
    "ils_iterations": ILS_ITERATIONS_VALUES,
    "double_bridge_min_segment_size": DOUBLE_BRIDGE_MIN_SEGMENT_SIZE_VALUES,
    "edge_memory_evaporation_rate": EDGE_MEMORY_EVAPORATION_RATE_VALUES,
    "edge_memory_max": EDGE_MEMORY_MAX_VALUES,
    "global_best_deposit": GLOBAL_BEST_DEPOSIT_VALUES,
    "near_best_deposit": NEAR_BEST_DEPOSIT_VALUES,
    "near_best_gap": NEAR_BEST_GAP_VALUES,
    "memory_max_edge_moves": MEMORY_MAX_EDGE_MOVES_VALUES,
    "memory_top_k_edges": MEMORY_TOP_K_EDGES_VALUES,
    "memory_candidate_pool_size": MEMORY_CANDIDATE_POOL_SIZE_VALUES,
    "use_distance_weighted_memory": USE_DISTANCE_WEIGHTED_MEMORY_VALUES,
    "case_a_mode": CASE_A_MODE_VALUES,
    "case_b_mode": CASE_B_MODE_VALUES,
    "case_b_memory_moves": CASE_B_MEMORY_MOVES_VALUES,
    "case_b_memory_top_k_edges": CASE_B_MEMORY_TOP_K_EDGES_VALUES,
    "case_b_similarity_threshold": CASE_B_SIMILARITY_THRESHOLD_VALUES,
    "case_b_mini_reconstruction_size": CASE_B_MINI_RECONSTRUCTION_SIZE_VALUES,
    "use_candidate_lists": USE_CANDIDATE_LISTS_VALUES,
    "candidate_list_size": CANDIDATE_LIST_SIZE_VALUES,
    "candidate_list_apply_to_2opt": CANDIDATE_LIST_APPLY_TO_2OPT_VALUES,
    "candidate_list_apply_to_3opt": CANDIDATE_LIST_APPLY_TO_3OPT_VALUES,
}

BASE_RUN_ARGUMENTS = {
    "coordinates",
    "population_size",
    "max_iterations",
    "seed",
    "rho",
    "temperature_start",
    "temperature_min",
    "use_integer_distances",
}


def choose_tuning_benchmark(selected_benchmark=None):
    if selected_benchmark is not None:
        if selected_benchmark not in BENCHMARKS:
            raise SystemExit("Unknown benchmark: " + selected_benchmark)
        return selected_benchmark

    if TUNING_BENCHMARK is not None:
        if TUNING_BENCHMARK not in BENCHMARKS:
            raise SystemExit("Unknown benchmark: " + TUNING_BENCHMARK)
        return TUNING_BENCHMARK

    try:
        from main import BENCHMARK_MENU
    except ImportError:
        return "wi29"

    for benchmark_name in BENCHMARKS:
        if BENCHMARK_MENU.get(benchmark_name) == True:
            return benchmark_name

    return "wi29"


def make_parameter_tuning_paths(benchmark_name, ana_experiment, search_name):
    if search_name is None:
        search_name = "fixed_budget_" + ana_experiment

    parameter_tuning_directory = os.path.join(
        "results",
        benchmark_name,
        "parameter_tuning",
        "current",
        ana_experiment,
        search_name,
    )
    trials_file = os.path.join(parameter_tuning_directory, "trials.csv")
    best_file = os.path.join(parameter_tuning_directory, "best.csv")
    validation_file = os.path.join(parameter_tuning_directory, "validation_runs.csv")
    return parameter_tuning_directory, trials_file, best_file, validation_file


def active_parameter_names(ana_algorithm):
    signature = inspect.signature(ana_algorithm.run_ana)
    active_names = []

    for parameter_name in PARAMETER_DEFAULTS:
        if parameter_name in signature.parameters or parameter_name == "max_iterations":
            active_names.append(parameter_name)

    return active_names


def unsupported_required_parameters(ana_algorithm):
    signature = inspect.signature(ana_algorithm.run_ana)
    supported = BASE_RUN_ARGUMENTS.union(PARAMETER_DEFAULTS)
    unsupported = []

    for parameter_name, parameter in signature.parameters.items():
        if parameter_name in supported:
            continue
        if parameter.default is inspect.Parameter.empty:
            unsupported.append(parameter_name)

    return unsupported


def parse_value(parameter_name, value_text):
    if value_text == "None":
        return None
    if parameter_name in (
        "use_distance_weighted_memory",
        "use_candidate_lists",
        "candidate_list_apply_to_2opt",
        "candidate_list_apply_to_3opt",
    ):
        if value_text == "True":
            return True
        if value_text == "False":
            return False
        raise SystemExit("Expected True or False for: " + parameter_name)
    if parameter_name in ("case_a_mode", "case_b_mode"):
        return value_text
    if parameter_name in (
        "population_size",
        "max_iterations",
        "archive_size",
        "tabu_tenure",
        "tabu_max_steps",
        "tabu_no_improvement_limit",
        "tabu_candidate_sample_size",
        "ils_iterations",
        "double_bridge_min_segment_size",
        "memory_max_edge_moves",
        "memory_top_k_edges",
        "memory_candidate_pool_size",
        "case_b_memory_moves",
        "case_b_memory_top_k_edges",
        "case_b_mini_reconstruction_size",
        "candidate_list_size",
    ):
        return int(value_text)
    return float(value_text)


def parse_parameter_assignments(assignments):
    parsed = {}

    for assignment in assignments:
        if "=" not in assignment:
            raise SystemExit("Expected parameter assignment name=value: " + assignment)

        name, value_text = assignment.split("=", 1)
        name = name.strip()
        value_text = value_text.strip()

        if name not in PARAMETER_DEFAULTS:
            raise SystemExit("Unknown parameter: " + name)

        parsed[name] = parse_value(name, value_text)

    return parsed


def parse_parameter_list(parameter_text):
    names = []

    for parameter_name in parameter_text.split(","):
        parameter_name = parameter_name.strip()
        if parameter_name == "":
            continue
        if parameter_name not in PARAMETER_DEFAULTS:
            raise SystemExit("Unknown parameter: " + parameter_name)
        names.append(parameter_name)

    return names


def make_initial_config(parameter_names, fixed_parameters=None):
    config = {}
    for parameter_name in parameter_names:
        config[parameter_name] = PARAMETER_DEFAULTS[parameter_name]

    if fixed_parameters is not None:
        for parameter_name, value in fixed_parameters.items():
            if parameter_name in config:
                config[parameter_name] = value

    return config


def config_key(config):
    return tuple(config[parameter_name] for parameter_name in config)


def max_iterations_for(config):
    if "max_iterations" in config:
        return config["max_iterations"]
    return TOTAL_ANT_UPDATES // config["population_size"]


def is_temperature_valid(config):
    ana_temperature_valid = config["temperature_min"] < config["temperature_start"]
    two_opt_temperature_valid = True
    if (
        "two_opt_trigger_temperature_start" in config
        and "two_opt_trigger_temperature_min" in config
    ):
        two_opt_temperature_valid = (
            config["two_opt_trigger_temperature_min"]
            < config["two_opt_trigger_temperature_start"]
        )
    return ana_temperature_valid and two_opt_temperature_valid


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


def neighbor_config(current_config, rng, tunable_parameters=None):
    if tunable_parameters is None:
        parameters = list(current_config.keys())
    else:
        parameters = [
            parameter_name
            for parameter_name in tunable_parameters
            if parameter_name in current_config
        ]

    if len(parameters) == 0:
        return current_config.copy(), "none"

    for attempt in range(100):
        changed_parameter = rng.choice(parameters)
        candidate = current_config.copy()

        candidate[changed_parameter] = move_one_position(
            current_config[changed_parameter],
            PARAMETER_VALUES[changed_parameter],
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

    if len(gap_values) == 1:
        standard_deviation = 0.0
    else:
        standard_deviation = statistics.stdev(gap_values)

    return {
        "best_gap_percent": min(gap_values),
        "mean_gap_percent": statistics.mean(gap_values),
        "worst_gap_percent": max(gap_values),
        "gap_standard_deviation": standard_deviation,
    }


def run_algorithm(ana_algorithm, coordinates, config, max_iterations, seed, benchmark):
    arguments = {
        "coordinates": coordinates,
        "population_size": config["population_size"],
        "max_iterations": max_iterations,
        "seed": seed,
        "rho": config["rho"],
        "temperature_start": config["temperature_start"],
        "temperature_min": config["temperature_min"],
        "use_integer_distances": benchmark["use_integer_distances"],
    }
    arguments.update(config)

    signature = inspect.signature(ana_algorithm.run_ana)
    accepted_arguments = {}
    for argument_name, argument_value in arguments.items():
        if argument_name in signature.parameters:
            accepted_arguments[argument_name] = argument_value

    return ana_algorithm.run_ana(**accepted_arguments)


def config_summary_fields(config, max_iterations, ana_experiment):
    summary = {
        "ana_experiment": ana_experiment,
        "population_size": config["population_size"],
        "max_iterations": max_iterations,
        "total_ant_updates": config["population_size"] * max_iterations,
    }

    for parameter_name in config:
        summary[parameter_name] = config[parameter_name]

    return summary


def evaluate_config(config, coordinates, benchmark, ana_algorithm, ana_experiment, cache):
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
        result = run_algorithm(
            ana_algorithm,
            coordinates,
            config,
            max_iterations,
            seed,
            benchmark,
        )

        if result is None:
            invalid = True
            break

        if not ana_algorithm.is_valid_route(result["best_route"], len(coordinates)):
            invalid = True
            break

        best_fitness = result["best_fitness"]
        if benchmark["use_integer_distances"]:
            best_fitness = int(best_fitness)
        fitness_values.append(best_fitness)

    runtime_seconds = time.perf_counter() - start_time

    if invalid:
        summary = config_summary_fields(config, max_iterations, ana_experiment)
        summary.update(
            {
                "mean_fitness": math.inf,
                "best_gap_percent": math.inf,
                "mean_gap_percent": math.inf,
                "worst_gap_percent": math.inf,
                "gap_standard_deviation": math.inf,
                "score": math.inf,
                "runtime_seconds": runtime_seconds,
                "cache_hit": "no",
            }
        )
    else:
        gap_statistics = calculate_gap_statistics(
            fitness_values,
            benchmark["known_optimum"],
        )
        score = (
            gap_statistics["mean_gap_percent"]
            + 0.25 * gap_statistics["gap_standard_deviation"]
        )

        summary = config_summary_fields(config, max_iterations, ana_experiment)
        summary.update(
            {
                "mean_fitness": statistics.mean(fitness_values),
                "best_gap_percent": gap_statistics["best_gap_percent"],
                "mean_gap_percent": gap_statistics["mean_gap_percent"],
                "worst_gap_percent": gap_statistics["worst_gap_percent"],
                "gap_standard_deviation": gap_statistics["gap_standard_deviation"],
                "score": score,
                "runtime_seconds": runtime_seconds,
                "cache_hit": "no",
            }
        )

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


def tune_parameters(tuning_benchmark, ana_experiment, tunable_parameters=None,
                    fixed_parameters=None):
    os.makedirs("results", exist_ok=True)

    ana_algorithm = load_ana_algorithm(ana_experiment)
    if ana_algorithm is None:
        return None, []

    unsupported = unsupported_required_parameters(ana_algorithm)
    if len(unsupported) > 0:
        print("Cannot tune", ana_experiment, "because run_ana requires:")
        print(", ".join(unsupported))
        return None, []

    benchmark = BENCHMARKS[tuning_benchmark]
    coordinates = load_benchmark_coordinates(tuning_benchmark, benchmark)
    if coordinates is None:
        print("Could not load benchmark:", tuning_benchmark)
        return None, []

    rng = random.Random(TUNING_RANDOM_SEED)
    cache = {}
    trial_rows = []
    parameter_names = active_parameter_names(ana_algorithm)

    if tunable_parameters is not None:
        unsupported_tunable = []
        for parameter_name in tunable_parameters:
            if parameter_name not in parameter_names:
                unsupported_tunable.append(parameter_name)
        if len(unsupported_tunable) > 0:
            print("These parameters are not active for", ana_experiment + ":")
            print(", ".join(unsupported_tunable))
            return None, []

    current_config = make_initial_config(parameter_names, fixed_parameters)
    current_result = evaluate_config(
        current_config,
        coordinates,
        benchmark,
        ana_algorithm,
        ana_experiment,
        cache,
    )
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
        candidate_config, changed_parameter = neighbor_config(
            current_config,
            rng,
            tunable_parameters,
        )
        temperature = tuning_temperature(trial_number)
        candidate_result = evaluate_config(
            candidate_config,
            coordinates,
            benchmark,
            ana_algorithm,
            ana_experiment,
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

    return best_config, best_result, trial_rows, coordinates, benchmark, ana_algorithm


def validate_best_config(best_config, coordinates, benchmark, ana_algorithm,
                         ana_experiment):
    rows = []
    max_iterations = max_iterations_for(best_config)

    for seed in VALIDATION_SEEDS:
        start_time = time.perf_counter()
        result = run_algorithm(
            ana_algorithm,
            coordinates,
            best_config,
            max_iterations,
            seed,
            benchmark,
        )
        runtime_seconds = time.perf_counter() - start_time

        valid_route = "yes"
        if result is None:
            valid_route = "no"
            best_fitness = math.inf
            gap_percent = math.inf
        elif not ana_algorithm.is_valid_route(result["best_route"], len(coordinates)):
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
                "ana_experiment": ana_experiment,
                "population_size": best_config["population_size"],
                "max_iterations": max_iterations,
                "total_ant_updates": best_config["population_size"]
                * max_iterations,
                "best_fitness": best_fitness,
                "known_optimum": benchmark["known_optimum"],
                "gap_percent": gap_percent,
                "valid_route": valid_route,
                "runtime_seconds": runtime_seconds,
            }
        )
        for parameter_name in best_config:
            rows[-1][parameter_name] = best_config[parameter_name]

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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Tune ANA parameters for one version on one benchmark.",
    )
    parser.add_argument(
        "--ana-experiment",
        "--version",
        default=ANA_EXPERIMENT,
        help=(
            "ANA version to tune, for example v1, v4, or v5. "
            "Available now: " + ", ".join(available_ana_experiments())
        ),
    )
    parser.add_argument(
        "--benchmark",
        default=TUNING_BENCHMARK,
        help="Benchmark to tune on. Available: " + ", ".join(BENCHMARKS.keys()),
    )
    parser.add_argument(
        "--search-name",
        default=PARAMETER_SEARCH_NAME,
        help="Result folder name under the selected version.",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=TUNING_TRIALS,
        help="Number of simulated-annealing tuning trials.",
    )
    parser.add_argument(
        "--total-ant-updates",
        type=int,
        default=TOTAL_ANT_UPDATES,
        help="Fixed budget used to derive max_iterations from population_size.",
    )
    parser.add_argument(
        "--tune-only",
        default=DEFAULT_TUNE_ONLY,
        help=(
            "Comma-separated active parameters that may move, for example "
            "archive_min_edge_diversity or archive_size,archive_near_best_gap."
        ),
    )
    parser.add_argument(
        "--fixed",
        action="append",
        default=[],
        help=(
            "Fix or override a parameter with name=value. Can be repeated, "
            "for example --fixed archive_size=5."
        ),
    )
    return parser.parse_args()


def parameter_fieldnames(best_config):
    names = []
    for parameter_name in PARAMETER_DEFAULTS:
        if parameter_name in best_config and parameter_name != "max_iterations":
            names.append(parameter_name)
    return names


def main():
    global TOTAL_ANT_UPDATES
    global TUNING_TRIALS

    arguments = parse_arguments()
    ana_experiment = arguments.ana_experiment
    tuning_benchmark = choose_tuning_benchmark(arguments.benchmark)
    tunable_parameters = None
    if arguments.tune_only is not None:
        tunable_parameters = parse_parameter_list(arguments.tune_only)
    fixed_parameters = parse_parameter_assignments(arguments.fixed)
    TOTAL_ANT_UPDATES = arguments.total_ant_updates
    TUNING_TRIALS = arguments.trials

    tuning_paths = make_parameter_tuning_paths(
        tuning_benchmark,
        ana_experiment,
        arguments.search_name,
    )
    parameter_tuning_directory = tuning_paths[0]
    trials_file = tuning_paths[1]
    best_file = tuning_paths[2]
    validation_file = tuning_paths[3]

    if (
        os.path.exists(trials_file)
        or os.path.exists(best_file)
        or os.path.exists(validation_file)
    ):
        print("Parameter tuning results already exist.")
        print("Use --search-name before running again.")
        print("Trials:", trials_file)
        print("Best:", best_file)
        print("Validation:", validation_file)
        return

    print("Tuning benchmark:", tuning_benchmark)
    print("ANA experiment:", ana_experiment)
    if tunable_parameters is not None:
        print("Tuning only:", ", ".join(tunable_parameters))
    if len(fixed_parameters) > 0:
        fixed_parts = []
        for parameter_name in sorted(fixed_parameters):
            fixed_parts.append(parameter_name + "=" + str(fixed_parameters[parameter_name]))
        print("Fixed parameters:", ", ".join(fixed_parts))

    tuning_result = tune_parameters(
        tuning_benchmark,
        ana_experiment,
        tunable_parameters,
        fixed_parameters,
    )
    if tuning_result[0] is None:
        return

    best_config = tuning_result[0]
    best_result = tuning_result[1]
    trial_rows = tuning_result[2]
    coordinates = tuning_result[3]
    benchmark = tuning_result[4]
    ana_algorithm = tuning_result[5]
    tuned_parameter_fieldnames = parameter_fieldnames(best_config)

    trial_fieldnames = [
        "trial_number",
        "changed_parameter",
        "ana_experiment",
        "max_iterations",
    ]
    trial_fieldnames.extend(tuned_parameter_fieldnames)
    trial_fieldnames.extend([
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
    ])
    os.makedirs(parameter_tuning_directory, exist_ok=True)
    write_csv(trials_file, trial_rows, trial_fieldnames)

    validation_rows = validate_best_config(
        best_config,
        coordinates,
        benchmark,
        ana_algorithm,
        ana_experiment,
    )
    validation_fieldnames = [
        "seed",
        "ana_experiment",
        "max_iterations",
    ]
    validation_fieldnames.extend(tuned_parameter_fieldnames)
    validation_fieldnames.extend([
        "total_ant_updates",
        "best_fitness",
        "known_optimum",
        "gap_percent",
        "valid_route",
        "runtime_seconds",
    ])
    write_csv(validation_file, validation_rows, validation_fieldnames)

    best_row = best_result.copy()
    best_row["benchmark"] = tuning_benchmark
    best_row.update(validation_summary(validation_rows))

    best_fieldnames = [
        "benchmark",
        "ana_experiment",
        "max_iterations",
    ]
    best_fieldnames.extend(tuned_parameter_fieldnames)
    best_fieldnames.extend([
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
    ])
    write_csv(best_file, [best_row], best_fieldnames)

    print("Trials:", trials_file)
    print("Best:", best_file)
    print("Validation:", validation_file)


if __name__ == "__main__":
    main()
