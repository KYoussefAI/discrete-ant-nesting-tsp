import math

from core.tsp_utils import align_to_best
from core.tsp_utils import build_swap_sequence
from core.tsp_utils import introduce_edge_with_reversal
from core.tsp_utils import is_valid_route
from core.tsp_utils import normal_round
from core.tsp_utils import normalize_tour
from core.tsp_utils import random_segment_inversion
from core.tsp_utils import route_edges


def initialize_edge_memory(number_of_cities, edge_memory_initial):
    edge_memory = []
    for city_a in range(number_of_cities):
        row = []
        for city_b in range(number_of_cities):
            if city_a == city_b:
                row.append(0.0)
            else:
                row.append(edge_memory_initial)
        edge_memory.append(row)
    return edge_memory


def evaporate_edge_memory(edge_memory, evaporation_rate, edge_memory_max):
    evaporated_edges = 0
    retention = 1.0 - evaporation_rate
    for city_a in range(len(edge_memory)):
        for city_b in range(city_a + 1, len(edge_memory)):
            value = edge_memory[city_a][city_b] * retention
            if value > edge_memory_max:
                value = edge_memory_max
            edge_memory[city_a][city_b] = value
            edge_memory[city_b][city_a] = value
            evaporated_edges = evaporated_edges + 1
    return evaporated_edges


def deposit_route_edges(edge_memory, route, deposit_amount, edge_memory_max):
    deposited_edges = 0
    for edge in route_edges(route):
        city_a = edge[0]
        city_b = edge[1]
        value = edge_memory[city_a][city_b] + deposit_amount
        if value > edge_memory_max:
            value = edge_memory_max
        edge_memory[city_a][city_b] = value
        edge_memory[city_b][city_a] = value
        deposited_edges = deposited_edges + 1
    return deposited_edges


def precompute_memory_edge_pairs(distance_matrix):
    edge_pairs = []
    for city_a in range(len(distance_matrix)):
        for city_b in range(city_a + 1, len(distance_matrix)):
            distance_value = distance_matrix[city_a][city_b]
            inverse_distance = 1.0 / (distance_value + 0.000000000001)
            edge_pairs.append((city_a, city_b, distance_value, inverse_distance))
    return edge_pairs


def build_memory_ranked_edges(edge_memory, edge_pairs, use_distance_weighted_memory,
                              memory_candidate_pool_size):
    ranked_edges = []
    for edge_pair in edge_pairs:
        city_a = edge_pair[0]
        city_b = edge_pair[1]
        distance_value = edge_pair[2]
        inverse_distance = edge_pair[3]
        memory_value = edge_memory[city_a][city_b]
        if use_distance_weighted_memory:
            score = memory_value * inverse_distance
        else:
            score = memory_value
        ranked_edges.append((score, memory_value, distance_value, (city_a, city_b)))

    ranked_edges.sort(reverse=True)
    pool_size = min(memory_candidate_pool_size, len(ranked_edges))
    return ranked_edges[:pool_size]


def create_memory_rank_cache():
    return {
        "ranked_edges": [],
        "dirty": True,
        "rebuilds": 0,
        "dirty_rebuilds": 0,
    }


def mark_memory_dirty(memory_rank_cache):
    memory_rank_cache["dirty"] = True


def ensure_memory_ranked_edges(memory_rank_cache, edge_memory, edge_pairs,
                               use_distance_weighted_memory,
                               memory_candidate_pool_size):
    if not memory_rank_cache["dirty"]:
        return memory_rank_cache["ranked_edges"]

    ranked_edges = build_memory_ranked_edges(
        edge_memory,
        edge_pairs,
        use_distance_weighted_memory,
        memory_candidate_pool_size,
    )
    memory_rank_cache["ranked_edges"] = ranked_edges
    memory_rank_cache["dirty"] = False
    memory_rank_cache["rebuilds"] = memory_rank_cache["rebuilds"] + 1
    memory_rank_cache["dirty_rebuilds"] = memory_rank_cache["dirty_rebuilds"] + 1
    return ranked_edges


def positive_memory_guided_movement(route, memory_ranked_edges, dw, rng,
                                    memory_max_edge_moves, memory_top_k_edges):
    guided_route = normalize_tour(route)
    move_count = max(
        1,
        min(memory_max_edge_moves, int(abs(dw) * memory_max_edge_moves) + 1),
    )
    selected_edges = 0
    inserted_edges = 0
    failed_insertions = 0
    selected_this_movement = set()

    for move_number in range(move_count):
        current_edges = route_edges(guided_route)
        candidates = []
        for ranked_edge in memory_ranked_edges:
            edge = ranked_edge[3]
            if edge in current_edges:
                continue
            if edge in selected_this_movement:
                continue
            candidates.append(ranked_edge)
            if len(candidates) >= memory_top_k_edges:
                break

        if len(candidates) == 0:
            break

        selected = rng.choice(candidates)
        edge = selected[3]
        selected_this_movement.add(edge)
        selected_edges = selected_edges + 1

        candidate_route = introduce_edge_with_reversal(guided_route, edge)
        if (
            is_valid_route(candidate_route, len(route))
            and candidate_route[0] == 0
            and edge in route_edges(candidate_route)
        ):
            guided_route = candidate_route
            inserted_edges = inserted_edges + 1
        else:
            failed_insertions = failed_insertions + 1

    return {
        "route": normalize_tour(guided_route),
        "selected_edges": selected_edges,
        "inserted_edges": inserted_edges,
        "failed_insertions": failed_insertions,
    }


def negative_segment_inversion_movement(route, movement_strength, rng):
    return random_segment_inversion(route, movement_strength, rng)


def adaptive_memory_escape(current, rho, rng, r, memory_rank_cache, edge_memory,
                           memory_edge_pairs, use_distance_weighted_memory,
                           memory_candidate_pool_size, memory_top_k_edges,
                           case_a_stagnation_level_1,
                           case_a_stagnation_level_2,
                           iterations_since_global_best_improvement):
    if iterations_since_global_best_improvement < case_a_stagnation_level_1:
        moves = 1
    elif iterations_since_global_best_improvement < case_a_stagnation_level_2:
        moves = 2
    else:
        moves = 2

    memory_ranked_edges = ensure_memory_ranked_edges(
        memory_rank_cache,
        edge_memory,
        memory_edge_pairs,
        use_distance_weighted_memory,
        memory_candidate_pool_size,
    )
    memory_result = positive_memory_guided_movement(
        current,
        memory_ranked_edges,
        1.0,
        rng,
        moves,
        memory_top_k_edges,
    )
    if memory_result["inserted_edges"] > 0:
        return memory_result["route"], memory_result, True

    number_of_cities = len(current)
    maximum_moves = max(1, math.ceil(rho * (number_of_cities - 1)))
    movement_strength = max(1, normal_round(abs(r) * maximum_moves))
    return negative_segment_inversion_movement(current, movement_strength, rng), None, False


def mini_reconstruction(current, rng, memory_rank_cache, edge_memory,
                        memory_edge_pairs, use_distance_weighted_memory,
                        memory_candidate_pool_size, memory_top_k_edges,
                        case_b_mini_reconstruction_size):
    memory_ranked_edges = ensure_memory_ranked_edges(
        memory_rank_cache,
        edge_memory,
        memory_edge_pairs,
        use_distance_weighted_memory,
        memory_candidate_pool_size,
    )
    memory_result = positive_memory_guided_movement(
        current,
        memory_ranked_edges,
        1.0,
        rng,
        case_b_mini_reconstruction_size,
        memory_top_k_edges,
    )
    if memory_result["inserted_edges"] > 0:
        return memory_result["route"], memory_result, True

    return negative_segment_inversion_movement(current, 1, rng), None, False


def generate_ana_candidate(current, previous, best, current_fitness,
                           previous_fitness, best_fitness, rho, rng,
                           memory_rank_cache, edge_memory, memory_edge_pairs,
                           use_distance_weighted_memory,
                           memory_candidate_pool_size, memory_max_edge_moves,
                           memory_top_k_edges,
                           case_b_mini_reconstruction_size,
                           case_a_stagnation_level_1,
                           case_a_stagnation_level_2,
                           iterations_since_global_best_improvement):
    epsilon = 0.000000000001
    number_of_cities = len(current)
    r = random_ana_value(rng)

    if current == best:
        trial, memory_result, success = adaptive_memory_escape(
            current,
            rho,
            rng,
            r,
            memory_rank_cache,
            edge_memory,
            memory_edge_pairs,
            use_distance_weighted_memory,
            memory_candidate_pool_size,
            memory_top_k_edges,
            case_a_stagnation_level_1,
            case_a_stagnation_level_2,
            iterations_since_global_best_improvement,
        )
        return {
            "route": trial,
            "case_name": "case_a",
            "memory_result": memory_result,
            "operator_success": success,
        }

    if current == previous:
        trial, memory_result, success = mini_reconstruction(
            current,
            rng,
            memory_rank_cache,
            edge_memory,
            memory_edge_pairs,
            use_distance_weighted_memory,
            memory_candidate_pool_size,
            memory_top_k_edges,
            case_b_mini_reconstruction_size,
        )
        return {
            "route": trial,
            "case_name": "case_b",
            "memory_result": memory_result,
            "operator_success": success,
        }

    aligned_current = align_to_best(current, best)
    current_swaps = build_swap_sequence(aligned_current, best)
    if len(current_swaps) == 0:
        return {
            "route": current.copy(),
            "case_name": "general",
            "memory_result": None,
            "operator_success": True,
        }

    aligned_previous = align_to_best(previous, best)
    previous_swaps = build_swap_sequence(aligned_previous, best)
    s_current = len(current_swaps) / (number_of_cities - 1)
    s_previous = len(previous_swaps) / (number_of_cities - 1)
    q_current = max(0, current_fitness - best_fitness) / (current_fitness + epsilon)
    q_previous = max(0, previous_fitness - best_fitness) / (previous_fitness + epsilon)

    t_current = math.sqrt((s_current * s_current + q_current * q_current) / 2)
    t_previous = math.sqrt((s_previous * s_previous + q_previous * q_previous) / 2)
    tau = min(1, t_current / (t_previous + epsilon))
    dw = r * tau
    movement_strength = max(1, normal_round(abs(dw) * len(current_swaps)))

    if dw > 0:
        memory_ranked_edges = ensure_memory_ranked_edges(
            memory_rank_cache,
            edge_memory,
            memory_edge_pairs,
            use_distance_weighted_memory,
            memory_candidate_pool_size,
        )
        memory_result = positive_memory_guided_movement(
            current,
            memory_ranked_edges,
            dw,
            rng,
            memory_max_edge_moves,
            memory_top_k_edges,
        )
        return {
            "route": memory_result["route"],
            "case_name": "general",
            "memory_result": memory_result,
            "operator_success": True,
        }

    return {
        "route": negative_segment_inversion_movement(current, movement_strength, rng),
        "case_name": "general",
        "memory_result": None,
        "operator_success": True,
    }


def random_ana_value(rng):
    r = rng.uniform(-1.0, 1.0)
    while r == 0:
        r = rng.uniform(-1.0, 1.0)
    return r


def accept_with_sa(current_fitness, trial_fitness, temperature, rng):
    if trial_fitness <= current_fitness:
        return True
    epsilon = 0.000000000001
    delta = trial_fitness - current_fitness
    delta_normalized = delta / (current_fitness + epsilon)
    probability = math.exp(-delta_normalized / temperature)
    return rng.random() < probability


def temperature_at(iteration, max_iterations, temperature_start, temperature_min):
    if max_iterations <= 1:
        return temperature_min
    progress = iteration / (max_iterations - 1)
    return temperature_start + (temperature_min - temperature_start) * progress
