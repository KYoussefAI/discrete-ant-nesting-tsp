import random

from core.local_search import polish_with_two_opt_three_opt
from core.operators import accept_with_sa
from core.operators import create_memory_rank_cache
from core.operators import deposit_route_edges
from core.operators import evaporate_edge_memory
from core.operators import generate_ana_candidate
from core.operators import initialize_edge_memory
from core.operators import mark_memory_dirty
from core.operators import precompute_memory_edge_pairs
from core.operators import temperature_at
from core.tsp_utils import build_distance_matrix
from core.tsp_utils import create_initial_route
from core.tsp_utils import is_valid_route
from core.tsp_utils import normalize_tour
from core.tsp_utils import tour_cost


ALGORITHM_NAME = "edge_memory_ana"


def run_edge_memory_ana_tsp(coordinates, population_size=30,
                            max_iterations=1000, seed=1, rho=0.10,
                            temperature_start=0.05, temperature_min=0.001,
                            use_integer_distances=False,
                            edge_memory_initial=1.0,
                            edge_memory_evaporation_rate=0.02,
                            edge_memory_max=10.0,
                            global_best_deposit=1.0,
                            near_best_deposit=0.3,
                            near_best_gap=0.03,
                            memory_max_edge_moves=3,
                            memory_top_k_edges=20,
                            memory_candidate_pool_size=100,
                            use_distance_weighted_memory=True,
                            case_b_mini_reconstruction_size=3,
                            case_a_stagnation_level_1=500,
                            case_a_stagnation_level_2=1500):
    context = initialize_search(
        coordinates,
        population_size,
        seed,
        use_integer_distances,
        edge_memory_initial,
    )
    parameters = {
        "rho": rho,
        "edge_memory_evaporation_rate": edge_memory_evaporation_rate,
        "edge_memory_max": edge_memory_max,
        "global_best_deposit": global_best_deposit,
        "near_best_deposit": near_best_deposit,
        "near_best_gap": near_best_gap,
        "memory_max_edge_moves": memory_max_edge_moves,
        "memory_top_k_edges": memory_top_k_edges,
        "memory_candidate_pool_size": memory_candidate_pool_size,
        "use_distance_weighted_memory": use_distance_weighted_memory,
        "case_b_mini_reconstruction_size": case_b_mini_reconstruction_size,
        "case_a_stagnation_level_1": case_a_stagnation_level_1,
        "case_a_stagnation_level_2": case_a_stagnation_level_2,
    }

    deposit_initial_global_best_memory(context, parameters)

    for iteration in range(max_iterations):
        update_iteration_state(
            context,
            parameters,
            iteration,
            max_iterations,
            temperature_start,
            temperature_min,
        )

        for ant_index in range(population_size):
            candidate = generate_candidate_route(context, parameters, ant_index)
            accepted = accept_or_reject_candidate(context, candidate, ant_index)
            if accepted:
                update_ant_after_acceptance(context, candidate, ant_index)
                update_memory_from_near_best(context, parameters, candidate)
                if candidate_improves_global_best(context, candidate):
                    polished = polish_new_global_best(context, candidate)
                    update_global_best(context, parameters, polished, ant_index)

        record_iteration_history(context)

    return build_final_result(context)


def initialize_search(coordinates, population_size, seed, use_integer_distances,
                      edge_memory_initial):
    rng = random.Random(seed)
    number_of_cities = len(coordinates)
    distance_matrix = build_distance_matrix(coordinates, use_integer_distances)
    routes, previous_routes, fitnesses, previous_fitnesses = initialize_population(
        number_of_cities,
        population_size,
        distance_matrix,
        rng,
    )
    best_route, best_fitness = find_best_route(routes, fitnesses)

    return {
        "rng": rng,
        "number_of_cities": number_of_cities,
        "distance_matrix": distance_matrix,
        "memory_edge_pairs": precompute_memory_edge_pairs(distance_matrix),
        "routes": routes,
        "previous_routes": previous_routes,
        "fitnesses": fitnesses,
        "previous_fitnesses": previous_fitnesses,
        "best_route": best_route,
        "best_fitness": best_fitness,
        "edge_memory": initialize_edge_memory(number_of_cities, edge_memory_initial),
        "memory_rank_cache": create_memory_rank_cache(),
        "history": [best_fitness],
        "temperature": None,
        "iterations_since_global_best_improvement": 0,
        "stats": create_empty_stats(population_size),
    }


def initialize_population(number_of_cities, population_size, distance_matrix, rng):
    routes = []
    previous_routes = []
    fitnesses = []
    previous_fitnesses = []
    for ant in range(population_size):
        route = create_initial_route(number_of_cities, rng)
        fitness = tour_cost(route, distance_matrix)
        routes.append(route.copy())
        previous_routes.append(route.copy())
        fitnesses.append(fitness)
        previous_fitnesses.append(fitness)
    return routes, previous_routes, fitnesses, previous_fitnesses


def find_best_route(routes, fitnesses):
    best_route = routes[0].copy()
    best_fitness = fitnesses[0]
    for index in range(1, len(routes)):
        if fitnesses[index] < best_fitness:
            best_route = routes[index].copy()
            best_fitness = fitnesses[index]
    return best_route, best_fitness


def deposit_initial_global_best_memory(context, parameters):
    deposit_global_best_memory(context, parameters)


def update_iteration_state(context, parameters, iteration, max_iterations,
                           temperature_start, temperature_min):
    stats = context["stats"]
    stats["edge_memory_evaporations"] = (
        stats["edge_memory_evaporations"]
        + evaporate_edge_memory(
            context["edge_memory"],
            parameters["edge_memory_evaporation_rate"],
            parameters["edge_memory_max"],
        )
    )
    mark_memory_dirty(context["memory_rank_cache"])
    deposit_global_best_memory(context, parameters)
    context["temperature"] = temperature_at(
        iteration,
        max_iterations,
        temperature_start,
        temperature_min,
    )


def generate_candidate_route(context, parameters, ant_index):
    candidate = generate_ana_candidate(
        context["routes"][ant_index],
        context["previous_routes"][ant_index],
        context["best_route"],
        context["fitnesses"][ant_index],
        context["previous_fitnesses"][ant_index],
        context["best_fitness"],
        parameters["rho"],
        context["rng"],
        context["memory_rank_cache"],
        context["edge_memory"],
        context["memory_edge_pairs"],
        parameters["use_distance_weighted_memory"],
        parameters["memory_candidate_pool_size"],
        parameters["memory_max_edge_moves"],
        parameters["memory_top_k_edges"],
        parameters["case_b_mini_reconstruction_size"],
        parameters["case_a_stagnation_level_1"],
        parameters["case_a_stagnation_level_2"],
        context["iterations_since_global_best_improvement"],
    )
    candidate["route"] = normalize_tour(candidate["route"])
    if not is_valid_route(candidate["route"], context["number_of_cities"]):
        raise ValueError("Invalid route created by ANA movement")

    candidate["fitness"] = tour_cost(candidate["route"], context["distance_matrix"])
    count_candidate_diagnostics(context, candidate)
    return candidate


def accept_or_reject_candidate(context, candidate, ant_index):
    context["stats"]["total_fitness_evaluations"] = (
        context["stats"]["total_fitness_evaluations"] + 1
    )
    accepted = accept_with_sa(
        context["fitnesses"][ant_index],
        candidate["fitness"],
        context["temperature"],
        context["rng"],
    )

    if accepted and candidate["fitness"] > context["fitnesses"][ant_index]:
        context["stats"]["accepted_worse"] = context["stats"]["accepted_worse"] + 1
    if not accepted and candidate["fitness"] > context["fitnesses"][ant_index]:
        context["stats"]["rejected_worse"] = context["stats"]["rejected_worse"] + 1

    return accepted


def update_ant_after_acceptance(context, candidate, ant_index):
    context["previous_routes"][ant_index] = context["routes"][ant_index].copy()
    context["previous_fitnesses"][ant_index] = context["fitnesses"][ant_index]
    context["routes"][ant_index] = candidate["route"].copy()
    context["fitnesses"][ant_index] = candidate["fitness"]


def update_memory_from_near_best(context, parameters, candidate):
    if candidate["fitness"] > context["best_fitness"] * (1.0 + parameters["near_best_gap"]):
        return

    context["stats"]["edge_memory_deposits"] = (
        context["stats"]["edge_memory_deposits"]
        + deposit_route_edges(
            context["edge_memory"],
            candidate["route"],
            parameters["near_best_deposit"],
            parameters["edge_memory_max"],
        )
    )
    context["stats"]["memory_near_best_deposits"] = (
        context["stats"]["memory_near_best_deposits"] + 1
    )
    mark_memory_dirty(context["memory_rank_cache"])


def candidate_improves_global_best(context, candidate):
    return candidate["fitness"] < context["best_fitness"]


def polish_new_global_best(context, candidate):
    polish_result = polish_with_two_opt_three_opt(
        candidate["route"],
        context["distance_matrix"],
    )
    count_polish_diagnostics(context, polish_result)
    if not is_valid_route(polish_result["route"], context["number_of_cities"]):
        raise ValueError("Invalid route created by local search")
    return polish_result


def update_global_best(context, parameters, polished, ant_index):
    context["routes"][ant_index] = polished["route"].copy()
    context["fitnesses"][ant_index] = polished["fitness"]
    context["best_route"] = polished["route"].copy()
    context["best_fitness"] = polished["fitness"]
    context["iterations_since_global_best_improvement"] = 0
    deposit_global_best_memory(context, parameters)


def record_iteration_history(context):
    context["history"].append(context["best_fitness"])
    context["iterations_since_global_best_improvement"] = (
        context["iterations_since_global_best_improvement"] + 1
    )


def build_final_result(context):
    stats = context["stats"]
    stats["memory_ranked_pool_rebuilds"] = context["memory_rank_cache"]["rebuilds"]
    stats["memory_dirty_rebuilds"] = context["memory_rank_cache"]["dirty_rebuilds"]

    result = {
        "best_route": context["best_route"],
        "best_fitness": context["best_fitness"],
        "history": context["history"],
    }
    result.update(stats)
    return result


def deposit_global_best_memory(context, parameters):
    context["stats"]["edge_memory_deposits"] = (
        context["stats"]["edge_memory_deposits"]
        + deposit_route_edges(
            context["edge_memory"],
            context["best_route"],
            parameters["global_best_deposit"],
            parameters["edge_memory_max"],
        )
    )
    context["stats"]["memory_global_best_deposits"] = (
        context["stats"]["memory_global_best_deposits"] + 1
    )
    mark_memory_dirty(context["memory_rank_cache"])


def count_candidate_diagnostics(context, candidate):
    stats = context["stats"]
    case_name = candidate["case_name"]
    stats[case_name] = stats[case_name] + 1

    if case_name == "case_a":
        stats["case_a_calls"] = stats["case_a_calls"] + 1
        if candidate["operator_success"]:
            stats["case_a_successes"] = stats["case_a_successes"] + 1
        else:
            stats["case_a_fallbacks"] = stats["case_a_fallbacks"] + 1

    if case_name == "case_b":
        stats["case_b_calls"] = stats["case_b_calls"] + 1
        if candidate["operator_success"]:
            stats["case_b_successes"] = stats["case_b_successes"] + 1
        else:
            stats["case_b_fallbacks"] = stats["case_b_fallbacks"] + 1

    memory_result = candidate["memory_result"]
    if memory_result is None:
        return
    stats["memory_guided_moves"] = stats["memory_guided_moves"] + 1
    stats["memory_selected_edges"] = (
        stats["memory_selected_edges"] + memory_result["selected_edges"]
    )
    stats["memory_inserted_edges"] = (
        stats["memory_inserted_edges"] + memory_result["inserted_edges"]
    )
    stats["memory_failed_insertions"] = (
        stats["memory_failed_insertions"] + memory_result["failed_insertions"]
    )


def count_polish_diagnostics(context, polish_result):
    stats = context["stats"]
    stats["two_opt_calls"] = stats["two_opt_calls"] + polish_result["two_opt_calls"]
    stats["two_opt_candidate_checks"] = (
        stats["two_opt_candidate_checks"]
        + polish_result["two_opt_candidate_checks"]
    )
    stats["two_opt_improvements"] = (
        stats["two_opt_improvements"] + polish_result["two_opt_improvements"]
    )
    stats["three_opt_calls"] = (
        stats["three_opt_calls"] + polish_result["three_opt_calls"]
    )
    stats["three_opt_edge_triples_checked"] = (
        stats["three_opt_edge_triples_checked"]
        + polish_result["three_opt_edge_triples_checked"]
    )
    stats["three_opt_reconnections_checked"] = (
        stats["three_opt_reconnections_checked"]
        + polish_result["three_opt_reconnections_checked"]
    )
    stats["three_opt_improvements"] = (
        stats["three_opt_improvements"] + polish_result["three_opt_improvements"]
    )
    stats["total_fitness_evaluations"] = (
        stats["total_fitness_evaluations"] + polish_result["fitness_evaluations"]
    )


def create_empty_stats(population_size):
    return {
        "accepted_worse": 0,
        "rejected_worse": 0,
        "case_a": 0,
        "case_b": 0,
        "general": 0,
        "two_opt_calls": 0,
        "two_opt_candidate_checks": 0,
        "two_opt_improvements": 0,
        "three_opt_calls": 0,
        "three_opt_edge_triples_checked": 0,
        "three_opt_reconnections_checked": 0,
        "three_opt_improvements": 0,
        "edge_memory_deposits": 0,
        "edge_memory_evaporations": 0,
        "memory_guided_moves": 0,
        "memory_selected_edges": 0,
        "memory_inserted_edges": 0,
        "memory_failed_insertions": 0,
        "memory_near_best_deposits": 0,
        "memory_global_best_deposits": 0,
        "memory_ranked_pool_rebuilds": 0,
        "memory_dirty_rebuilds": 0,
        "case_a_calls": 0,
        "case_a_successes": 0,
        "case_a_fallbacks": 0,
        "case_b_calls": 0,
        "case_b_successes": 0,
        "case_b_fallbacks": 0,
        "total_fitness_evaluations": population_size,
    }
