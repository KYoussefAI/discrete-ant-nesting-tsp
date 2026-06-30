import csv
import importlib
import inspect
import os
import statistics
import time

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
}


def available_ana_experiments():
    experiments = ["baseline"]
    experiments_directory = "experiments"

    if not os.path.isdir(experiments_directory):
        return experiments

    for file_name in os.listdir(experiments_directory):
        if not file_name.startswith("ana_tsp_v") or not file_name.endswith(".py"):
            continue

        version = file_name[len("ana_tsp_"):-len(".py")]
        if not version.startswith("v") or not version[1:].isdigit():
            continue
        if version not in experiments:
            experiments.append(version)

    def sort_key(experiment):
        if experiment == "baseline":
            return (0, 0)
        if experiment.startswith("v") and experiment[1:].isdigit():
            return (1, int(experiment[1:]))
        return (2, experiment)

    experiments.sort(key=sort_key)
    return experiments


def load_ana_algorithm(ana_experiment):
    try:
        if ana_experiment == "baseline":
            return importlib.import_module("ana_tsp")
        if ana_experiment.startswith("v") and ana_experiment[1:].isdigit():
            return importlib.import_module("experiments.ana_tsp_" + ana_experiment)
    except ImportError:
        print("ANA experiment is not available yet:", ana_experiment)
        return None

    print("Unknown ANA experiment:", ana_experiment)
    print("Allowed values are:", ", ".join(available_ana_experiments()))
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
    three_opt_calls = 0
    three_opt_edge_triples_checked = 0
    three_opt_reconnections_checked = 0
    three_opt_improvements = 0
    two_opt_calls = 0
    two_opt_trigger_attempts = 0
    two_opt_trigger_accepted = 0
    two_opt_trigger_rejected = 0
    two_opt_forced_calls = 0
    two_opt_probabilistic_calls = 0
    two_opt_candidate_checks = 0
    two_opt_improvements = 0
    archive_insert_attempts = 0
    archive_insertions = 0
    archive_replacements = 0
    archive_rejected_similar = 0
    archive_rejected_quality = 0
    archive_final_sizes = []
    teacher_global_best_choices = 0
    teacher_archive_choices = 0
    mean_archive_edge_diversities = []
    tabu_calls = 0
    tabu_steps = 0
    tabu_candidate_checks = 0
    tabu_admissible_moves = 0
    tabu_moves_accepted = 0
    tabu_improving_moves = 0
    tabu_worse_moves = 0
    tabu_aspiration_overrides = 0
    tabu_best_improvements = 0
    tabu_stops_max_steps = 0
    tabu_stops_no_improvement = 0
    tabu_stops_no_admissible_move = 0
    ils_calls = 0
    ils_perturbations = 0
    ils_polish_calls = 0
    ils_improvements = 0
    vnd_calls = 0
    vnd_restarts = 0
    vnd_2opt_improvements = 0
    vnd_relocate_improvements = 0
    vnd_swap_improvements = 0
    vnd_oropt2_improvements = 0
    vnd_oropt3_improvements = 0
    vnd_3opt_improvements = 0
    vnd_candidate_checks = 0
    edge_memory_deposits = 0
    edge_memory_evaporations = 0
    memory_guided_moves = 0
    memory_selected_edges = 0
    memory_inserted_edges = 0
    memory_failed_insertions = 0
    memory_near_best_deposits = 0
    memory_global_best_deposits = 0
    mean_selected_edge_memories = []
    mean_selected_edge_distances = []
    memory_ranked_pool_rebuilds = 0
    memory_ranked_pool_sizes = []
    memory_pair_scans_saved_estimate = 0
    memory_dirty_rebuilds = 0
    memory_selection_random_choices = 0
    memory_selection_greedy_choices = 0
    case_a_operator_calls = 0
    case_a_operator_successes = 0
    case_a_operator_fallbacks = 0
    case_a_operator_inserted_edges = 0
    case_a_operator_invalid_routes = 0
    case_a_memory_complement_calls = 0
    case_a_memory_complement_insertions = 0
    case_a_memory_complement_fallbacks = 0
    case_a_suspicious_calls = 0
    case_a_suspicious_insertions = 0
    case_a_suspicious_fallbacks = 0
    case_a_adaptive_calls = 0
    case_a_adaptive_level_0 = 0
    case_a_adaptive_level_1 = 0
    case_a_adaptive_level_2 = 0
    case_a_adaptive_insertions = 0
    case_a_adaptive_fallbacks = 0
    case_a_safe_calls = 0
    case_a_safe_insertions = 0
    case_a_safe_fallbacks = 0
    case_a_safe_invalid_routes = 0
    case_a_double_bridge_calls = 0
    case_a_double_bridge_successes = 0
    case_a_double_bridge_fallbacks = 0
    case_a_ga_lite_calls = 0
    case_a_ga_lite_successes = 0
    case_a_ga_lite_fallbacks = 0
    case_a_ga_lite_parent2_population = 0
    case_a_ga_lite_parent2_memory = 0
    total_fitness_evaluations = 0

    for row in run_rows:
        fitness_values.append(row["best_fitness"])
        gap_values.append(row["gap_percent"])
        runtime_values.append(row["runtime_seconds"])
        three_opt_calls = three_opt_calls + row["three_opt_calls"]
        three_opt_edge_triples_checked = (
            three_opt_edge_triples_checked + row["three_opt_edge_triples_checked"]
        )
        three_opt_reconnections_checked = (
            three_opt_reconnections_checked
            + row["three_opt_reconnections_checked"]
        )
        three_opt_improvements = (
            three_opt_improvements + row["three_opt_improvements"]
        )
        two_opt_calls = two_opt_calls + row["two_opt_calls"]
        two_opt_trigger_attempts = (
            two_opt_trigger_attempts + row["two_opt_trigger_attempts"]
        )
        two_opt_trigger_accepted = (
            two_opt_trigger_accepted + row["two_opt_trigger_accepted"]
        )
        two_opt_trigger_rejected = (
            two_opt_trigger_rejected + row["two_opt_trigger_rejected"]
        )
        two_opt_forced_calls = (
            two_opt_forced_calls + row["two_opt_forced_calls"]
        )
        two_opt_probabilistic_calls = (
            two_opt_probabilistic_calls + row["two_opt_probabilistic_calls"]
        )
        two_opt_candidate_checks = (
            two_opt_candidate_checks + row["two_opt_candidate_checks"]
        )
        two_opt_improvements = two_opt_improvements + row["two_opt_improvements"]
        archive_insert_attempts = (
            archive_insert_attempts + row["archive_insert_attempts"]
        )
        archive_insertions = archive_insertions + row["archive_insertions"]
        archive_replacements = archive_replacements + row["archive_replacements"]
        archive_rejected_similar = (
            archive_rejected_similar + row["archive_rejected_similar"]
        )
        archive_rejected_quality = (
            archive_rejected_quality + row["archive_rejected_quality"]
        )
        archive_final_sizes.append(row["archive_final_size"])
        teacher_global_best_choices = (
            teacher_global_best_choices + row["teacher_global_best_choices"]
        )
        teacher_archive_choices = (
            teacher_archive_choices + row["teacher_archive_choices"]
        )
        mean_archive_edge_diversities.append(row["mean_archive_edge_diversity"])
        tabu_calls = tabu_calls + row["tabu_calls"]
        tabu_steps = tabu_steps + row["tabu_steps"]
        tabu_candidate_checks = tabu_candidate_checks + row["tabu_candidate_checks"]
        tabu_admissible_moves = (
            tabu_admissible_moves + row["tabu_admissible_moves"]
        )
        tabu_moves_accepted = tabu_moves_accepted + row["tabu_moves_accepted"]
        tabu_improving_moves = tabu_improving_moves + row["tabu_improving_moves"]
        tabu_worse_moves = tabu_worse_moves + row["tabu_worse_moves"]
        tabu_aspiration_overrides = (
            tabu_aspiration_overrides + row["tabu_aspiration_overrides"]
        )
        tabu_best_improvements = (
            tabu_best_improvements + row["tabu_best_improvements"]
        )
        tabu_stops_max_steps = (
            tabu_stops_max_steps + row["tabu_stops_max_steps"]
        )
        tabu_stops_no_improvement = (
            tabu_stops_no_improvement + row["tabu_stops_no_improvement"]
        )
        tabu_stops_no_admissible_move = (
            tabu_stops_no_admissible_move
            + row["tabu_stops_no_admissible_move"]
        )
        ils_calls = ils_calls + row["ils_calls"]
        ils_perturbations = ils_perturbations + row["ils_perturbations"]
        ils_polish_calls = ils_polish_calls + row["ils_polish_calls"]
        ils_improvements = ils_improvements + row["ils_improvements"]
        vnd_calls = vnd_calls + row["vnd_calls"]
        vnd_restarts = vnd_restarts + row["vnd_restarts"]
        vnd_2opt_improvements = (
            vnd_2opt_improvements + row["vnd_2opt_improvements"]
        )
        vnd_relocate_improvements = (
            vnd_relocate_improvements + row["vnd_relocate_improvements"]
        )
        vnd_swap_improvements = (
            vnd_swap_improvements + row["vnd_swap_improvements"]
        )
        vnd_oropt2_improvements = (
            vnd_oropt2_improvements + row["vnd_oropt2_improvements"]
        )
        vnd_oropt3_improvements = (
            vnd_oropt3_improvements + row["vnd_oropt3_improvements"]
        )
        vnd_3opt_improvements = (
            vnd_3opt_improvements + row["vnd_3opt_improvements"]
        )
        vnd_candidate_checks = (
            vnd_candidate_checks + row["vnd_candidate_checks"]
        )
        edge_memory_deposits = (
            edge_memory_deposits + row["edge_memory_deposits"]
        )
        edge_memory_evaporations = (
            edge_memory_evaporations + row["edge_memory_evaporations"]
        )
        memory_guided_moves = (
            memory_guided_moves + row["memory_guided_moves"]
        )
        memory_selected_edges = (
            memory_selected_edges + row["memory_selected_edges"]
        )
        memory_inserted_edges = (
            memory_inserted_edges + row["memory_inserted_edges"]
        )
        memory_failed_insertions = (
            memory_failed_insertions + row["memory_failed_insertions"]
        )
        memory_near_best_deposits = (
            memory_near_best_deposits + row["memory_near_best_deposits"]
        )
        memory_global_best_deposits = (
            memory_global_best_deposits + row["memory_global_best_deposits"]
        )
        mean_selected_edge_memories.append(row["mean_selected_edge_memory"])
        mean_selected_edge_distances.append(row["mean_selected_edge_distance"])
        memory_ranked_pool_rebuilds = (
            memory_ranked_pool_rebuilds + row["memory_ranked_pool_rebuilds"]
        )
        memory_ranked_pool_sizes.append(row["memory_ranked_pool_size"])
        memory_pair_scans_saved_estimate = (
            memory_pair_scans_saved_estimate
            + row["memory_pair_scans_saved_estimate"]
        )
        memory_dirty_rebuilds = (
            memory_dirty_rebuilds + row["memory_dirty_rebuilds"]
        )
        memory_selection_random_choices = (
            memory_selection_random_choices
            + row["memory_selection_random_choices"]
        )
        memory_selection_greedy_choices = (
            memory_selection_greedy_choices
            + row["memory_selection_greedy_choices"]
        )
        case_a_operator_calls = (
            case_a_operator_calls + row["case_a_operator_calls"]
        )
        case_a_operator_successes = (
            case_a_operator_successes + row["case_a_operator_successes"]
        )
        case_a_operator_fallbacks = (
            case_a_operator_fallbacks + row["case_a_operator_fallbacks"]
        )
        case_a_operator_inserted_edges = (
            case_a_operator_inserted_edges
            + row["case_a_operator_inserted_edges"]
        )
        case_a_operator_invalid_routes = (
            case_a_operator_invalid_routes
            + row["case_a_operator_invalid_routes"]
        )
        case_a_memory_complement_calls = (
            case_a_memory_complement_calls
            + row["case_a_memory_complement_calls"]
        )
        case_a_memory_complement_insertions = (
            case_a_memory_complement_insertions
            + row["case_a_memory_complement_insertions"]
        )
        case_a_memory_complement_fallbacks = (
            case_a_memory_complement_fallbacks
            + row["case_a_memory_complement_fallbacks"]
        )
        case_a_suspicious_calls = (
            case_a_suspicious_calls + row["case_a_suspicious_calls"]
        )
        case_a_suspicious_insertions = (
            case_a_suspicious_insertions
            + row["case_a_suspicious_insertions"]
        )
        case_a_suspicious_fallbacks = (
            case_a_suspicious_fallbacks + row["case_a_suspicious_fallbacks"]
        )
        case_a_adaptive_calls = (
            case_a_adaptive_calls + row["case_a_adaptive_calls"]
        )
        case_a_adaptive_level_0 = (
            case_a_adaptive_level_0 + row["case_a_adaptive_level_0"]
        )
        case_a_adaptive_level_1 = (
            case_a_adaptive_level_1 + row["case_a_adaptive_level_1"]
        )
        case_a_adaptive_level_2 = (
            case_a_adaptive_level_2 + row["case_a_adaptive_level_2"]
        )
        case_a_adaptive_insertions = (
            case_a_adaptive_insertions + row["case_a_adaptive_insertions"]
        )
        case_a_adaptive_fallbacks = (
            case_a_adaptive_fallbacks + row["case_a_adaptive_fallbacks"]
        )
        case_a_safe_calls = case_a_safe_calls + row["case_a_safe_calls"]
        case_a_safe_insertions = (
            case_a_safe_insertions + row["case_a_safe_insertions"]
        )
        case_a_safe_fallbacks = (
            case_a_safe_fallbacks + row["case_a_safe_fallbacks"]
        )
        case_a_safe_invalid_routes = (
            case_a_safe_invalid_routes + row["case_a_safe_invalid_routes"]
        )
        case_a_double_bridge_calls = (
            case_a_double_bridge_calls + row["case_a_double_bridge_calls"]
        )
        case_a_double_bridge_successes = (
            case_a_double_bridge_successes
            + row["case_a_double_bridge_successes"]
        )
        case_a_double_bridge_fallbacks = (
            case_a_double_bridge_fallbacks
            + row["case_a_double_bridge_fallbacks"]
        )
        case_a_ga_lite_calls = (
            case_a_ga_lite_calls + row["case_a_ga_lite_calls"]
        )
        case_a_ga_lite_successes = (
            case_a_ga_lite_successes + row["case_a_ga_lite_successes"]
        )
        case_a_ga_lite_fallbacks = (
            case_a_ga_lite_fallbacks + row["case_a_ga_lite_fallbacks"]
        )
        case_a_ga_lite_parent2_population = (
            case_a_ga_lite_parent2_population
            + row["case_a_ga_lite_parent2_population"]
        )
        case_a_ga_lite_parent2_memory = (
            case_a_ga_lite_parent2_memory
            + row["case_a_ga_lite_parent2_memory"]
        )
        total_fitness_evaluations = (
            total_fitness_evaluations + row["total_fitness_evaluations"]
        )
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
        "two_opt_trigger_temperature_start": (
            run_rows[0]["two_opt_trigger_temperature_start"]
        ),
        "two_opt_trigger_temperature_min": (
            run_rows[0]["two_opt_trigger_temperature_min"]
        ),
        "local_search_mode": run_rows[0]["local_search_mode"],
        "tabu_tenure": run_rows[0]["tabu_tenure"],
        "tabu_max_steps": run_rows[0]["tabu_max_steps"],
        "tabu_no_improvement_limit": run_rows[0]["tabu_no_improvement_limit"],
        "tabu_candidate_sample_size": run_rows[0]["tabu_candidate_sample_size"],
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
        "three_opt_calls": three_opt_calls,
        "three_opt_edge_triples_checked": three_opt_edge_triples_checked,
        "three_opt_reconnections_checked": three_opt_reconnections_checked,
        "three_opt_improvements": three_opt_improvements,
        "two_opt_calls": two_opt_calls,
        "two_opt_trigger_attempts": two_opt_trigger_attempts,
        "two_opt_trigger_accepted": two_opt_trigger_accepted,
        "two_opt_trigger_rejected": two_opt_trigger_rejected,
        "two_opt_forced_calls": two_opt_forced_calls,
        "two_opt_probabilistic_calls": two_opt_probabilistic_calls,
        "two_opt_candidate_checks": two_opt_candidate_checks,
        "two_opt_improvements": two_opt_improvements,
        "use_candidate_lists": run_rows[0].get("use_candidate_lists", ""),
        "candidate_list_size": run_rows[0].get("candidate_list_size", ""),
        "candidate_list_apply_to_2opt": run_rows[0].get(
            "candidate_list_apply_to_2opt",
            "",
        ),
        "candidate_list_apply_to_3opt": run_rows[0].get(
            "candidate_list_apply_to_3opt",
            "",
        ),
        "candidate_list_2opt_checks_skipped": sum(
            row.get("candidate_list_2opt_checks_skipped", 0) for row in run_rows
        ),
        "candidate_list_2opt_checks_evaluated": sum(
            row.get("candidate_list_2opt_checks_evaluated", 0) for row in run_rows
        ),
        "candidate_list_3opt_reconnections_skipped": sum(
            row.get("candidate_list_3opt_reconnections_skipped", 0)
            for row in run_rows
        ),
        "candidate_list_3opt_reconnections_evaluated": sum(
            row.get("candidate_list_3opt_reconnections_evaluated", 0)
            for row in run_rows
        ),
        "candidate_list_total_skipped": sum(
            row.get("candidate_list_total_skipped", 0) for row in run_rows
        ),
        "candidate_list_total_evaluated": sum(
            row.get("candidate_list_total_evaluated", 0) for row in run_rows
        ),
        "archive_insert_attempts": archive_insert_attempts,
        "archive_insertions": archive_insertions,
        "archive_replacements": archive_replacements,
        "archive_rejected_similar": archive_rejected_similar,
        "archive_rejected_quality": archive_rejected_quality,
        "archive_final_size": statistics.mean(archive_final_sizes),
        "teacher_global_best_choices": teacher_global_best_choices,
        "teacher_archive_choices": teacher_archive_choices,
        "mean_archive_edge_diversity": statistics.mean(
            mean_archive_edge_diversities
        ),
        "tabu_calls": tabu_calls,
        "tabu_steps": tabu_steps,
        "tabu_candidate_checks": tabu_candidate_checks,
        "tabu_admissible_moves": tabu_admissible_moves,
        "tabu_moves_accepted": tabu_moves_accepted,
        "tabu_improving_moves": tabu_improving_moves,
        "tabu_worse_moves": tabu_worse_moves,
        "tabu_aspiration_overrides": tabu_aspiration_overrides,
        "tabu_best_improvements": tabu_best_improvements,
        "tabu_stops_max_steps": tabu_stops_max_steps,
        "tabu_stops_no_improvement": tabu_stops_no_improvement,
        "tabu_stops_no_admissible_move": tabu_stops_no_admissible_move,
        "ils_calls": ils_calls,
        "ils_perturbations": ils_perturbations,
        "ils_polish_calls": ils_polish_calls,
        "ils_improvements": ils_improvements,
        "vnd_calls": vnd_calls,
        "vnd_restarts": vnd_restarts,
        "vnd_2opt_improvements": vnd_2opt_improvements,
        "vnd_relocate_improvements": vnd_relocate_improvements,
        "vnd_swap_improvements": vnd_swap_improvements,
        "vnd_oropt2_improvements": vnd_oropt2_improvements,
        "vnd_oropt3_improvements": vnd_oropt3_improvements,
        "vnd_3opt_improvements": vnd_3opt_improvements,
        "vnd_candidate_checks": vnd_candidate_checks,
        "edge_memory_deposits": edge_memory_deposits,
        "edge_memory_evaporations": edge_memory_evaporations,
        "memory_guided_moves": memory_guided_moves,
        "memory_selected_edges": memory_selected_edges,
        "memory_inserted_edges": memory_inserted_edges,
        "memory_failed_insertions": memory_failed_insertions,
        "memory_near_best_deposits": memory_near_best_deposits,
        "memory_global_best_deposits": memory_global_best_deposits,
        "mean_selected_edge_memory": statistics.mean(
            mean_selected_edge_memories
        ),
        "mean_selected_edge_distance": statistics.mean(
            mean_selected_edge_distances
        ),
        "memory_ranked_pool_rebuilds": memory_ranked_pool_rebuilds,
        "memory_ranked_pool_size": statistics.mean(memory_ranked_pool_sizes),
        "memory_pair_scans_saved_estimate": memory_pair_scans_saved_estimate,
        "memory_dirty_rebuilds": memory_dirty_rebuilds,
        "memory_selection_random_choices": memory_selection_random_choices,
        "memory_selection_greedy_choices": memory_selection_greedy_choices,
        "case_a_mode": run_rows[0]["case_a_mode"],
        "case_b_mode": run_rows[0]["case_b_mode"],
        "case_b_operator_calls": sum(
            row["case_b_operator_calls"] for row in run_rows
        ),
        "case_b_operator_successes": sum(
            row["case_b_operator_successes"] for row in run_rows
        ),
        "case_b_operator_fallbacks": sum(
            row["case_b_operator_fallbacks"] for row in run_rows
        ),
        "case_b_operator_inserted_edges": sum(
            row["case_b_operator_inserted_edges"] for row in run_rows
        ),
        "case_b_operator_invalid_routes": sum(
            row["case_b_operator_invalid_routes"] for row in run_rows
        ),
        "case_b_mini_reconstruction_calls": sum(
            row["case_b_mini_reconstruction_calls"] for row in run_rows
        ),
        "case_b_mini_reconstruction_insertions": sum(
            row["case_b_mini_reconstruction_insertions"] for row in run_rows
        ),
        "case_b_mini_reconstruction_fallbacks": sum(
            row["case_b_mini_reconstruction_fallbacks"] for row in run_rows
        ),
        "case_b_mini_reconstruction_invalid_routes": sum(
            row["case_b_mini_reconstruction_invalid_routes"] for row in run_rows
        ),
        "case_a_operator_calls": case_a_operator_calls,
        "case_a_operator_successes": case_a_operator_successes,
        "case_a_operator_fallbacks": case_a_operator_fallbacks,
        "case_a_operator_inserted_edges": case_a_operator_inserted_edges,
        "case_a_operator_invalid_routes": case_a_operator_invalid_routes,
        "case_a_memory_complement_calls": case_a_memory_complement_calls,
        "case_a_memory_complement_insertions": (
            case_a_memory_complement_insertions
        ),
        "case_a_memory_complement_fallbacks": (
            case_a_memory_complement_fallbacks
        ),
        "case_a_suspicious_calls": case_a_suspicious_calls,
        "case_a_suspicious_insertions": case_a_suspicious_insertions,
        "case_a_suspicious_fallbacks": case_a_suspicious_fallbacks,
        "case_a_adaptive_calls": case_a_adaptive_calls,
        "case_a_adaptive_level_0": case_a_adaptive_level_0,
        "case_a_adaptive_level_1": case_a_adaptive_level_1,
        "case_a_adaptive_level_2": case_a_adaptive_level_2,
        "case_a_adaptive_insertions": case_a_adaptive_insertions,
        "case_a_adaptive_fallbacks": case_a_adaptive_fallbacks,
        "case_a_safe_calls": case_a_safe_calls,
        "case_a_safe_insertions": case_a_safe_insertions,
        "case_a_safe_fallbacks": case_a_safe_fallbacks,
        "case_a_safe_invalid_routes": case_a_safe_invalid_routes,
        "case_a_double_bridge_calls": case_a_double_bridge_calls,
        "case_a_double_bridge_successes": case_a_double_bridge_successes,
        "case_a_double_bridge_fallbacks": case_a_double_bridge_fallbacks,
        "case_a_ga_lite_calls": case_a_ga_lite_calls,
        "case_a_ga_lite_successes": case_a_ga_lite_successes,
        "case_a_ga_lite_fallbacks": case_a_ga_lite_fallbacks,
        "case_a_ga_lite_parent2_population": (
            case_a_ga_lite_parent2_population
        ),
        "case_a_ga_lite_parent2_memory": case_a_ga_lite_parent2_memory,
        "iterations_since_global_best_improvement_final": run_rows[-1][
            "iterations_since_global_best_improvement_final"
        ],
        "total_fitness_evaluations": total_fitness_evaluations,
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
    if "two_opt_trigger_temperature_start" in parameters:
        print(
            "2-opt trigger temperature start:",
            parameters["two_opt_trigger_temperature_start"],
        )
        print(
            "2-opt trigger temperature minimum:",
            parameters["two_opt_trigger_temperature_min"],
        )
    if "tabu_tenure" in parameters:
        print("Tabu tenure:", parameters["tabu_tenure"])
        print("Tabu max steps:", parameters["tabu_max_steps"])
        print(
            "Tabu no-improvement limit:",
            parameters["tabu_no_improvement_limit"],
        )
        print(
            "Tabu candidate sample size:",
            parameters["tabu_candidate_sample_size"],
        )
    if "case_a_mode" in parameters:
        print("Case A mode:", parameters["case_a_mode"])
    if "case_b_mode" in parameters:
        print("Case B mode:", parameters["case_b_mode"])
    if "use_candidate_lists" in parameters:
        print("Use candidate lists:", parameters["use_candidate_lists"])
        print("Candidate list size:", parameters["candidate_list_size"])
        print(
            "Candidate lists apply to 2-opt:",
            parameters["candidate_list_apply_to_2opt"],
        )
        print(
            "Candidate lists apply to 3-opt:",
            parameters["candidate_list_apply_to_3opt"],
        )
    for parameter_name in (
        "edge_memory_evaporation_rate",
        "edge_memory_max",
        "global_best_deposit",
        "near_best_deposit",
        "near_best_gap",
        "memory_max_edge_moves",
        "memory_top_k_edges",
        "memory_candidate_pool_size",
        "use_distance_weighted_memory",
    ):
        if parameter_name in parameters:
            print(parameter_name + ":", parameters[parameter_name])


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
    two_opt_trigger_temperature_start = parameters.get(
        "two_opt_trigger_temperature_start",
        "",
    )
    two_opt_trigger_temperature_min = parameters.get(
        "two_opt_trigger_temperature_min",
        "",
    )
    local_search_mode = parameters.get("local_search_mode", "")
    tabu_tenure = parameters.get("tabu_tenure", "")
    tabu_max_steps = parameters.get("tabu_max_steps", "")
    tabu_no_improvement_limit = parameters.get("tabu_no_improvement_limit", "")
    tabu_candidate_sample_size = parameters.get("tabu_candidate_sample_size", "")
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
        if ana_experiment == "v4":
            result = ana_algorithm.run_ana(
                coordinates,
                population_size,
                max_iterations,
                seed,
                rho,
                temperature_start,
                temperature_min,
                two_opt_trigger_temperature_start,
                two_opt_trigger_temperature_min,
                use_integer_distances,
            )
        else:
            run_arguments = {
                "coordinates": coordinates,
                "population_size": population_size,
                "max_iterations": max_iterations,
                "seed": seed,
                "rho": rho,
                "temperature_start": temperature_start,
                "temperature_min": temperature_min,
                "use_integer_distances": use_integer_distances,
            }
            if local_search_mode != "":
                run_arguments["local_search_mode"] = local_search_mode
            for parameter_name in (
                "tabu_tenure",
                "tabu_max_steps",
                "tabu_no_improvement_limit",
                "tabu_candidate_sample_size",
                "edge_memory_initial",
                "edge_memory_evaporation_rate",
                "edge_memory_max",
                "global_best_deposit",
                "near_best_deposit",
                "near_best_gap",
                "memory_max_edge_moves",
                "memory_top_k_edges",
                "memory_candidate_pool_size",
                "use_distance_weighted_memory",
                "use_candidate_lists",
                "candidate_list_size",
                "candidate_list_apply_to_2opt",
                "candidate_list_apply_to_3opt",
                "case_a_mode",
                "case_b_mode",
                "case_b_memory_moves",
                "case_b_memory_top_k_edges",
                "case_b_similarity_threshold",
                "case_b_mini_reconstruction_size",
                "case_a_memory_escape_moves",
                "case_a_safe_memory_moves",
                "case_a_memory_top_k_edges",
                "case_a_suspicious_top_k",
                "case_a_suspicious_moves",
                "case_a_stagnation_level_1",
                "case_a_stagnation_level_2",
                "case_a_double_bridge_min_segment_size",
            ):
                if parameter_name in parameters:
                    run_arguments[parameter_name] = parameters[parameter_name]
            signature = inspect.signature(ana_algorithm.run_ana)
            accepted_arguments = {}
            for argument_name, argument_value in run_arguments.items():
                if argument_name in signature.parameters:
                    accepted_arguments[argument_name] = argument_value
            result = ana_algorithm.run_ana(**accepted_arguments)
        runtime = time.perf_counter() - start_time

        if not ana_algorithm.is_valid_route(result["best_route"], number_of_cities):
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
        total_fitness_evaluations = result.get(
            "total_fitness_evaluations",
            function_evaluations,
        )

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
            "two_opt_trigger_temperature_start": two_opt_trigger_temperature_start,
            "two_opt_trigger_temperature_min": two_opt_trigger_temperature_min,
            "local_search_mode": local_search_mode,
            "tabu_tenure": tabu_tenure,
            "tabu_max_steps": tabu_max_steps,
            "tabu_no_improvement_limit": tabu_no_improvement_limit,
            "tabu_candidate_sample_size": tabu_candidate_sample_size,
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
            "three_opt_calls": result.get("three_opt_calls", 0),
            "three_opt_edge_triples_checked": result.get(
                "three_opt_edge_triples_checked",
                0,
            ),
            "three_opt_reconnections_checked": result.get(
                "three_opt_reconnections_checked",
                0,
            ),
            "three_opt_improvements": result.get("three_opt_improvements", 0),
            "two_opt_calls": result.get("two_opt_calls", 0),
            "two_opt_trigger_attempts": result.get("two_opt_trigger_attempts", 0),
            "two_opt_trigger_accepted": result.get("two_opt_trigger_accepted", 0),
            "two_opt_trigger_rejected": result.get("two_opt_trigger_rejected", 0),
            "two_opt_forced_calls": result.get("two_opt_forced_calls", 0),
            "two_opt_probabilistic_calls": result.get(
                "two_opt_probabilistic_calls",
                0,
            ),
            "two_opt_candidate_checks": result.get("two_opt_candidate_checks", 0),
            "two_opt_improvements": result.get("two_opt_improvements", 0),
            "use_candidate_lists": result.get("use_candidate_lists", ""),
            "candidate_list_size": result.get("candidate_list_size", ""),
            "candidate_list_apply_to_2opt": result.get(
                "candidate_list_apply_to_2opt",
                "",
            ),
            "candidate_list_apply_to_3opt": result.get(
                "candidate_list_apply_to_3opt",
                "",
            ),
            "candidate_list_2opt_checks_skipped": result.get(
                "candidate_list_2opt_checks_skipped",
                0,
            ),
            "candidate_list_2opt_checks_evaluated": result.get(
                "candidate_list_2opt_checks_evaluated",
                0,
            ),
            "candidate_list_3opt_reconnections_skipped": result.get(
                "candidate_list_3opt_reconnections_skipped",
                0,
            ),
            "candidate_list_3opt_reconnections_evaluated": result.get(
                "candidate_list_3opt_reconnections_evaluated",
                0,
            ),
            "candidate_list_total_skipped": result.get(
                "candidate_list_total_skipped",
                0,
            ),
            "candidate_list_total_evaluated": result.get(
                "candidate_list_total_evaluated",
                0,
            ),
            "archive_insert_attempts": result.get("archive_insert_attempts", 0),
            "archive_insertions": result.get("archive_insertions", 0),
            "archive_replacements": result.get("archive_replacements", 0),
            "archive_rejected_similar": result.get("archive_rejected_similar", 0),
            "archive_rejected_quality": result.get("archive_rejected_quality", 0),
            "archive_final_size": result.get("archive_final_size", 0),
            "teacher_global_best_choices": result.get(
                "teacher_global_best_choices",
                0,
            ),
            "teacher_archive_choices": result.get("teacher_archive_choices", 0),
            "mean_archive_edge_diversity": result.get(
                "mean_archive_edge_diversity",
                0,
            ),
            "tabu_calls": result.get("tabu_calls", 0),
            "tabu_steps": result.get("tabu_steps", 0),
            "tabu_candidate_checks": result.get("tabu_candidate_checks", 0),
            "tabu_admissible_moves": result.get("tabu_admissible_moves", 0),
            "tabu_moves_accepted": result.get("tabu_moves_accepted", 0),
            "tabu_improving_moves": result.get("tabu_improving_moves", 0),
            "tabu_worse_moves": result.get("tabu_worse_moves", 0),
            "tabu_aspiration_overrides": result.get(
                "tabu_aspiration_overrides",
                0,
            ),
            "tabu_best_improvements": result.get("tabu_best_improvements", 0),
            "tabu_stops_max_steps": result.get("tabu_stops_max_steps", 0),
            "tabu_stops_no_improvement": result.get(
                "tabu_stops_no_improvement",
                0,
            ),
            "tabu_stops_no_admissible_move": result.get(
                "tabu_stops_no_admissible_move",
                0,
            ),
            "ils_calls": result.get("ils_calls", 0),
            "ils_perturbations": result.get("ils_perturbations", 0),
            "ils_polish_calls": result.get("ils_polish_calls", 0),
            "ils_improvements": result.get("ils_improvements", 0),
            "vnd_calls": result.get("vnd_calls", 0),
            "vnd_restarts": result.get("vnd_restarts", 0),
            "vnd_2opt_improvements": result.get("vnd_2opt_improvements", 0),
            "vnd_relocate_improvements": result.get(
                "vnd_relocate_improvements",
                0,
            ),
            "vnd_swap_improvements": result.get("vnd_swap_improvements", 0),
            "vnd_oropt2_improvements": result.get("vnd_oropt2_improvements", 0),
            "vnd_oropt3_improvements": result.get("vnd_oropt3_improvements", 0),
            "vnd_3opt_improvements": result.get("vnd_3opt_improvements", 0),
            "vnd_candidate_checks": result.get("vnd_candidate_checks", 0),
            "edge_memory_deposits": result.get("edge_memory_deposits", 0),
            "edge_memory_evaporations": result.get("edge_memory_evaporations", 0),
            "memory_guided_moves": result.get("memory_guided_moves", 0),
            "memory_selected_edges": result.get("memory_selected_edges", 0),
            "memory_inserted_edges": result.get("memory_inserted_edges", 0),
            "memory_failed_insertions": result.get("memory_failed_insertions", 0),
            "memory_near_best_deposits": result.get(
                "memory_near_best_deposits",
                0,
            ),
            "memory_global_best_deposits": result.get(
                "memory_global_best_deposits",
                0,
            ),
            "mean_selected_edge_memory": result.get(
                "mean_selected_edge_memory",
                0,
            ),
            "mean_selected_edge_distance": result.get(
                "mean_selected_edge_distance",
                0,
            ),
            "memory_ranked_pool_rebuilds": result.get(
                "memory_ranked_pool_rebuilds",
                0,
            ),
            "memory_ranked_pool_size": result.get("memory_ranked_pool_size", 0),
            "memory_pair_scans_saved_estimate": result.get(
                "memory_pair_scans_saved_estimate",
                0,
            ),
            "memory_dirty_rebuilds": result.get("memory_dirty_rebuilds", 0),
            "memory_selection_random_choices": result.get(
                "memory_selection_random_choices",
                0,
            ),
            "memory_selection_greedy_choices": result.get(
                "memory_selection_greedy_choices",
                0,
            ),
            "case_a_mode": result.get("case_a_mode", ""),
            "case_b_mode": result.get("case_b_mode", ""),
            "case_b_operator_calls": result.get("case_b_operator_calls", 0),
            "case_b_operator_successes": result.get(
                "case_b_operator_successes",
                0,
            ),
            "case_b_operator_fallbacks": result.get(
                "case_b_operator_fallbacks",
                0,
            ),
            "case_b_operator_inserted_edges": result.get(
                "case_b_operator_inserted_edges",
                0,
            ),
            "case_b_operator_invalid_routes": result.get(
                "case_b_operator_invalid_routes",
                0,
            ),
            "case_b_mini_reconstruction_calls": result.get(
                "case_b_mini_reconstruction_calls",
                0,
            ),
            "case_b_mini_reconstruction_insertions": result.get(
                "case_b_mini_reconstruction_insertions",
                0,
            ),
            "case_b_mini_reconstruction_fallbacks": result.get(
                "case_b_mini_reconstruction_fallbacks",
                0,
            ),
            "case_b_mini_reconstruction_invalid_routes": result.get(
                "case_b_mini_reconstruction_invalid_routes",
                0,
            ),
            "case_a_operator_calls": result.get("case_a_operator_calls", 0),
            "case_a_operator_successes": result.get(
                "case_a_operator_successes",
                0,
            ),
            "case_a_operator_fallbacks": result.get(
                "case_a_operator_fallbacks",
                0,
            ),
            "case_a_operator_inserted_edges": result.get(
                "case_a_operator_inserted_edges",
                0,
            ),
            "case_a_operator_invalid_routes": result.get(
                "case_a_operator_invalid_routes",
                0,
            ),
            "iterations_since_global_best_improvement_final": result.get(
                "iterations_since_global_best_improvement_final",
                0,
            ),
            "case_a_memory_complement_calls": result.get(
                "case_a_memory_complement_calls",
                0,
            ),
            "case_a_memory_complement_insertions": result.get(
                "case_a_memory_complement_insertions",
                0,
            ),
            "case_a_memory_complement_fallbacks": result.get(
                "case_a_memory_complement_fallbacks",
                0,
            ),
            "case_a_suspicious_calls": result.get("case_a_suspicious_calls", 0),
            "case_a_suspicious_insertions": result.get(
                "case_a_suspicious_insertions",
                0,
            ),
            "case_a_suspicious_fallbacks": result.get(
                "case_a_suspicious_fallbacks",
                0,
            ),
            "case_a_adaptive_calls": result.get("case_a_adaptive_calls", 0),
            "case_a_adaptive_level_0": result.get("case_a_adaptive_level_0", 0),
            "case_a_adaptive_level_1": result.get("case_a_adaptive_level_1", 0),
            "case_a_adaptive_level_2": result.get("case_a_adaptive_level_2", 0),
            "case_a_adaptive_insertions": result.get(
                "case_a_adaptive_insertions",
                0,
            ),
            "case_a_adaptive_fallbacks": result.get(
                "case_a_adaptive_fallbacks",
                0,
            ),
            "case_a_safe_calls": result.get("case_a_safe_calls", 0),
            "case_a_safe_insertions": result.get("case_a_safe_insertions", 0),
            "case_a_safe_fallbacks": result.get("case_a_safe_fallbacks", 0),
            "case_a_safe_invalid_routes": result.get(
                "case_a_safe_invalid_routes",
                0,
            ),
            "case_a_double_bridge_calls": result.get(
                "case_a_double_bridge_calls",
                0,
            ),
            "case_a_double_bridge_successes": result.get(
                "case_a_double_bridge_successes",
                0,
            ),
            "case_a_double_bridge_fallbacks": result.get(
                "case_a_double_bridge_fallbacks",
                0,
            ),
            "case_a_ga_lite_calls": result.get("case_a_ga_lite_calls", 0),
            "case_a_ga_lite_successes": result.get(
                "case_a_ga_lite_successes",
                0,
            ),
            "case_a_ga_lite_fallbacks": result.get(
                "case_a_ga_lite_fallbacks",
                0,
            ),
            "case_a_ga_lite_parent2_population": result.get(
                "case_a_ga_lite_parent2_population",
                0,
            ),
            "case_a_ga_lite_parent2_memory": result.get(
                "case_a_ga_lite_parent2_memory",
                0,
            ),
            "total_fitness_evaluations": total_fitness_evaluations,
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
        "two_opt_trigger_temperature_start",
        "two_opt_trigger_temperature_min",
        "local_search_mode",
        "tabu_tenure",
        "tabu_max_steps",
        "tabu_no_improvement_limit",
        "tabu_candidate_sample_size",
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
        "three_opt_calls",
        "three_opt_edge_triples_checked",
        "three_opt_reconnections_checked",
        "three_opt_improvements",
        "two_opt_calls",
        "two_opt_trigger_attempts",
        "two_opt_trigger_accepted",
        "two_opt_trigger_rejected",
        "two_opt_forced_calls",
        "two_opt_probabilistic_calls",
        "two_opt_candidate_checks",
        "two_opt_improvements",
        "use_candidate_lists",
        "candidate_list_size",
        "candidate_list_apply_to_2opt",
        "candidate_list_apply_to_3opt",
        "candidate_list_2opt_checks_skipped",
        "candidate_list_2opt_checks_evaluated",
        "candidate_list_3opt_reconnections_skipped",
        "candidate_list_3opt_reconnections_evaluated",
        "candidate_list_total_skipped",
        "candidate_list_total_evaluated",
        "archive_insert_attempts",
        "archive_insertions",
        "archive_replacements",
        "archive_rejected_similar",
        "archive_rejected_quality",
        "archive_final_size",
        "teacher_global_best_choices",
        "teacher_archive_choices",
        "mean_archive_edge_diversity",
        "tabu_calls",
        "tabu_steps",
        "tabu_candidate_checks",
        "tabu_admissible_moves",
        "tabu_moves_accepted",
        "tabu_improving_moves",
        "tabu_worse_moves",
        "tabu_aspiration_overrides",
        "tabu_best_improvements",
        "tabu_stops_max_steps",
        "tabu_stops_no_improvement",
        "tabu_stops_no_admissible_move",
        "ils_calls",
        "ils_perturbations",
        "ils_polish_calls",
        "ils_improvements",
        "vnd_calls",
        "vnd_restarts",
        "vnd_2opt_improvements",
        "vnd_relocate_improvements",
        "vnd_swap_improvements",
        "vnd_oropt2_improvements",
        "vnd_oropt3_improvements",
        "vnd_3opt_improvements",
        "vnd_candidate_checks",
        "edge_memory_deposits",
        "edge_memory_evaporations",
        "memory_guided_moves",
        "memory_selected_edges",
        "memory_inserted_edges",
        "memory_failed_insertions",
        "memory_near_best_deposits",
        "memory_global_best_deposits",
        "mean_selected_edge_memory",
        "mean_selected_edge_distance",
        "memory_ranked_pool_rebuilds",
        "memory_ranked_pool_size",
        "memory_pair_scans_saved_estimate",
        "memory_dirty_rebuilds",
        "memory_selection_random_choices",
        "memory_selection_greedy_choices",
        "case_a_mode",
        "case_b_mode",
        "case_b_operator_calls",
        "case_b_operator_successes",
        "case_b_operator_fallbacks",
        "case_b_operator_inserted_edges",
        "case_b_operator_invalid_routes",
        "case_b_mini_reconstruction_calls",
        "case_b_mini_reconstruction_insertions",
        "case_b_mini_reconstruction_fallbacks",
        "case_b_mini_reconstruction_invalid_routes",
        "case_a_operator_calls",
        "case_a_operator_successes",
        "case_a_operator_fallbacks",
        "case_a_operator_inserted_edges",
        "case_a_operator_invalid_routes",
        "iterations_since_global_best_improvement_final",
        "case_a_memory_complement_calls",
        "case_a_memory_complement_insertions",
        "case_a_memory_complement_fallbacks",
        "case_a_suspicious_calls",
        "case_a_suspicious_insertions",
        "case_a_suspicious_fallbacks",
        "case_a_adaptive_calls",
        "case_a_adaptive_level_0",
        "case_a_adaptive_level_1",
        "case_a_adaptive_level_2",
        "case_a_adaptive_insertions",
        "case_a_adaptive_fallbacks",
        "case_a_safe_calls",
        "case_a_safe_insertions",
        "case_a_safe_fallbacks",
        "case_a_safe_invalid_routes",
        "case_a_double_bridge_calls",
        "case_a_double_bridge_successes",
        "case_a_double_bridge_fallbacks",
        "case_a_ga_lite_calls",
        "case_a_ga_lite_successes",
        "case_a_ga_lite_fallbacks",
        "case_a_ga_lite_parent2_population",
        "case_a_ga_lite_parent2_memory",
        "total_fitness_evaluations",
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
        "two_opt_trigger_temperature_start",
        "two_opt_trigger_temperature_min",
        "local_search_mode",
        "tabu_tenure",
        "tabu_max_steps",
        "tabu_no_improvement_limit",
        "tabu_candidate_sample_size",
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
        "three_opt_calls",
        "three_opt_edge_triples_checked",
        "three_opt_reconnections_checked",
        "three_opt_improvements",
        "two_opt_calls",
        "two_opt_trigger_attempts",
        "two_opt_trigger_accepted",
        "two_opt_trigger_rejected",
        "two_opt_forced_calls",
        "two_opt_probabilistic_calls",
        "two_opt_candidate_checks",
        "two_opt_improvements",
        "use_candidate_lists",
        "candidate_list_size",
        "candidate_list_apply_to_2opt",
        "candidate_list_apply_to_3opt",
        "candidate_list_2opt_checks_skipped",
        "candidate_list_2opt_checks_evaluated",
        "candidate_list_3opt_reconnections_skipped",
        "candidate_list_3opt_reconnections_evaluated",
        "candidate_list_total_skipped",
        "candidate_list_total_evaluated",
        "archive_insert_attempts",
        "archive_insertions",
        "archive_replacements",
        "archive_rejected_similar",
        "archive_rejected_quality",
        "archive_final_size",
        "teacher_global_best_choices",
        "teacher_archive_choices",
        "mean_archive_edge_diversity",
        "tabu_calls",
        "tabu_steps",
        "tabu_candidate_checks",
        "tabu_admissible_moves",
        "tabu_moves_accepted",
        "tabu_improving_moves",
        "tabu_worse_moves",
        "tabu_aspiration_overrides",
        "tabu_best_improvements",
        "tabu_stops_max_steps",
        "tabu_stops_no_improvement",
        "tabu_stops_no_admissible_move",
        "ils_calls",
        "ils_perturbations",
        "ils_polish_calls",
        "ils_improvements",
        "vnd_calls",
        "vnd_restarts",
        "vnd_2opt_improvements",
        "vnd_relocate_improvements",
        "vnd_swap_improvements",
        "vnd_oropt2_improvements",
        "vnd_oropt3_improvements",
        "vnd_3opt_improvements",
        "vnd_candidate_checks",
        "edge_memory_deposits",
        "edge_memory_evaporations",
        "memory_guided_moves",
        "memory_selected_edges",
        "memory_inserted_edges",
        "memory_failed_insertions",
        "memory_near_best_deposits",
        "memory_global_best_deposits",
        "mean_selected_edge_memory",
        "mean_selected_edge_distance",
        "memory_ranked_pool_rebuilds",
        "memory_ranked_pool_size",
        "memory_pair_scans_saved_estimate",
        "memory_dirty_rebuilds",
        "memory_selection_random_choices",
        "memory_selection_greedy_choices",
        "case_a_mode",
        "case_b_mode",
        "case_b_operator_calls",
        "case_b_operator_successes",
        "case_b_operator_fallbacks",
        "case_b_operator_inserted_edges",
        "case_b_operator_invalid_routes",
        "case_b_mini_reconstruction_calls",
        "case_b_mini_reconstruction_insertions",
        "case_b_mini_reconstruction_fallbacks",
        "case_b_mini_reconstruction_invalid_routes",
        "case_a_operator_calls",
        "case_a_operator_successes",
        "case_a_operator_fallbacks",
        "case_a_operator_inserted_edges",
        "case_a_operator_invalid_routes",
        "iterations_since_global_best_improvement_final",
        "case_a_memory_complement_calls",
        "case_a_memory_complement_insertions",
        "case_a_memory_complement_fallbacks",
        "case_a_suspicious_calls",
        "case_a_suspicious_insertions",
        "case_a_suspicious_fallbacks",
        "case_a_adaptive_calls",
        "case_a_adaptive_level_0",
        "case_a_adaptive_level_1",
        "case_a_adaptive_level_2",
        "case_a_adaptive_insertions",
        "case_a_adaptive_fallbacks",
        "case_a_safe_calls",
        "case_a_safe_insertions",
        "case_a_safe_fallbacks",
        "case_a_safe_invalid_routes",
        "case_a_double_bridge_calls",
        "case_a_double_bridge_successes",
        "case_a_double_bridge_fallbacks",
        "case_a_ga_lite_calls",
        "case_a_ga_lite_successes",
        "case_a_ga_lite_fallbacks",
        "case_a_ga_lite_parent2_population",
        "case_a_ga_lite_parent2_memory",
        "total_fitness_evaluations",
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
