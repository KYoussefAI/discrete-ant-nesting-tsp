import math
import random
import itertools


def distance(point_a, point_b):
    x_difference = point_a[0] - point_b[0]
    y_difference = point_a[1] - point_b[1]
    return math.sqrt(x_difference ** 2 + y_difference ** 2)


def build_distance_matrix(coordinates, use_integer_distances=False):
    distance_matrix = []
    for point_a in coordinates:
        row = []
        for point_b in coordinates:
            distance_value = distance(point_a, point_b)
            if use_integer_distances:
                distance_value = normal_round(distance_value)
            row.append(distance_value)
        distance_matrix.append(row)
    return distance_matrix


def tour_cost(route, distance_matrix):
    total = 0
    number_of_cities = len(route)
    for index in range(number_of_cities):
        city_a = route[index]
        if index == number_of_cities - 1:
            city_b = route[0]
        else:
            city_b = route[index + 1]
        total = total + distance_matrix[city_a][city_b]
    return total


def normalize_tour(route):
    number_of_cities = len(route)
    zero_index = route.index(0)
    forward = []
    for offset in range(number_of_cities):
        index = (zero_index + offset) % number_of_cities
        forward.append(route[index])

    reverse = [0]
    for index in range(number_of_cities - 1, 0, -1):
        reverse.append(forward[index])

    if reverse < forward:
        return reverse
    return forward


def build_swap_sequence(current, target):
    working = current.copy()
    swaps = []

    positions = {}
    for index in range(len(working)):
        city = working[index]
        positions[city] = index

    for index in range(1, len(working)):
        if working[index] != target[index]:
            city_needed = target[index]
            swap_index = positions[city_needed]
            swaps.append((index, swap_index))

            old_city = working[index]
            working[index] = working[swap_index]
            working[swap_index] = old_city

            positions[working[swap_index]] = swap_index
            positions[working[index]] = index

    return swaps


def align_to_best(route, best_route):
    forward = normalize_tour(route)
    reverse = [0]
    for index in range(len(forward) - 1, 0, -1):
        reverse.append(forward[index])

    forward_swaps = build_swap_sequence(forward, best_route)
    reverse_swaps = build_swap_sequence(reverse, best_route)
    if len(reverse_swaps) < len(forward_swaps):
        return reverse
    return forward


def apply_first_swaps(route, swaps, number_of_swaps):
    new_route = route.copy()
    if number_of_swaps > len(swaps):
        number_of_swaps = len(swaps)

    for swap_number in range(number_of_swaps):
        index_a = swaps[swap_number][0]
        index_b = swaps[swap_number][1]
        old_city = new_route[index_a]
        new_route[index_a] = new_route[index_b]
        new_route[index_b] = old_city
    return new_route


def random_swaps(route, number_of_swaps, rng):
    new_route = route.copy()
    number_of_cities = len(new_route)
    for swap_number in range(number_of_swaps):
        index_a = rng.randint(1, number_of_cities - 1)
        index_b = rng.randint(1, number_of_cities - 1)
        while index_b == index_a:
            index_b = rng.randint(1, number_of_cities - 1)
        old_city = new_route[index_a]
        new_route[index_a] = new_route[index_b]
        new_route[index_b] = old_city
    return new_route


def inversion_length_from_strength(route, movement_strength):
    maximum_length = len(route) - 2
    if maximum_length < 2:
        return 2

    segment_length = movement_strength + 1
    if segment_length < 2:
        segment_length = 2
    if segment_length > maximum_length:
        segment_length = maximum_length
    return segment_length


def random_segment_inversion(route, movement_strength, rng):
    new_route = route.copy()
    segment_length = inversion_length_from_strength(route, movement_strength)
    first_index = rng.randint(1, len(route) - segment_length)
    last_index = first_index + segment_length
    new_route[first_index:last_index] = reversed(new_route[first_index:last_index])
    return normalize_tour(new_route)


def make_edge(city_a, city_b):
    if city_a < city_b:
        return (city_a, city_b)
    return (city_b, city_a)


def route_edges(route):
    edges = set()
    number_of_cities = len(route)
    for index in range(number_of_cities):
        city_a = route[index]
        city_b = route[(index + 1) % number_of_cities]
        edges.add(make_edge(city_a, city_b))
    return edges


def missing_best_edges(route, best_route):
    current_edges = route_edges(route)
    best_edges = route_edges(best_route)
    missing_edges = []

    for edge in best_edges:
        if edge not in current_edges:
            missing_edges.append(edge)

    return missing_edges


def introduce_edge_with_reversal(route, edge):
    city_a = edge[0]
    city_b = edge[1]
    position_a = route.index(city_a)
    position_b = route.index(city_b)

    if position_a > position_b:
        old_position = position_a
        position_a = position_b
        position_b = old_position

    new_route = route.copy()
    new_route[position_a + 1:position_b + 1] = reversed(
        new_route[position_a + 1:position_b + 1]
    )
    return normalize_tour(new_route)


def guide_by_best_edges(route, best_route, movement_strength, rng):
    guided_route = normalize_tour(route)
    missing_edges = missing_best_edges(guided_route, best_route)

    number_of_edges_to_add = movement_strength
    if number_of_edges_to_add > len(missing_edges):
        number_of_edges_to_add = len(missing_edges)

    for edge_number in range(number_of_edges_to_add):
        if len(missing_edges) == 0:
            break

        edge = rng.choice(missing_edges)
        guided_route = introduce_edge_with_reversal(guided_route, edge)
        missing_edges = missing_best_edges(guided_route, best_route)

    return normalize_tour(guided_route)


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
    number_of_cities = len(edge_memory)

    for city_a in range(number_of_cities):
        for city_b in range(city_a + 1, number_of_cities):
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
    number_of_cities = len(distance_matrix)

    for city_a in range(number_of_cities):
        for city_b in range(city_a + 1, number_of_cities):
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
        ranked_edges.append(
            (score, memory_value, distance_value, (city_a, city_b))
        )

    ranked_edges.sort(reverse=True)
    pool_size = min(memory_candidate_pool_size, len(ranked_edges))
    return ranked_edges[:pool_size]


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
    memory_rank_cache["dirty_rebuilds"] = (
        memory_rank_cache["dirty_rebuilds"] + 1
    )
    memory_rank_cache["pool_size_total"] = (
        memory_rank_cache["pool_size_total"] + len(ranked_edges)
    )
    return ranked_edges


def guide_by_memory_edges(route, memory_ranked_edges, dw, rng,
                          memory_max_edge_moves, memory_top_k_edges):
    guided_route = normalize_tour(route)
    move_count = max(
        1,
        min(
            memory_max_edge_moves,
            int(abs(dw) * memory_max_edge_moves) + 1,
        ),
    )
    selected_edges = 0
    inserted_edges = 0
    failed_insertions = 0
    selected_memory_total = 0.0
    selected_distance_total = 0.0
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
        selected_memory_total = selected_memory_total + selected[1]
        selected_distance_total = selected_distance_total + selected[2]

        candidate_route = introduce_edge_with_reversal(guided_route, edge)
        if (
            is_valid_route(candidate_route, len(route))
            and edge in route_edges(candidate_route)
            and candidate_route[0] == 0
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
        "selected_memory_total": selected_memory_total,
        "selected_distance_total": selected_distance_total,
    }


def two_opt_local_search(route, distance_matrix):
    current_route = normalize_tour(route)
    current_fitness = tour_cost(current_route, distance_matrix)
    candidate_checks = 0
    improvements = 0
    fitness_evaluations = 1
    improved = True

    while improved:
        improved = False
        number_of_cities = len(current_route)

        for start_index in range(1, number_of_cities - 1):
            if improved:
                break

            for end_index in range(start_index + 1, number_of_cities):
                if start_index == 1 and end_index == number_of_cities - 1:
                    continue

                candidate_checks = candidate_checks + 1
                fitness_evaluations = fitness_evaluations + 1

                before_start = current_route[start_index - 1]
                segment_start = current_route[start_index]
                segment_end = current_route[end_index]
                after_end = current_route[(end_index + 1) % number_of_cities]

                removed_edges = (
                    distance_matrix[before_start][segment_start]
                    + distance_matrix[segment_end][after_end]
                )
                added_edges = (
                    distance_matrix[before_start][segment_end]
                    + distance_matrix[segment_start][after_end]
                )
                candidate_fitness = current_fitness - removed_edges + added_edges

                if candidate_fitness < current_fitness:
                    candidate_route = current_route.copy()
                    candidate_route[start_index:end_index + 1] = reversed(
                        candidate_route[start_index:end_index + 1]
                    )
                    candidate_route = normalize_tour(candidate_route)
                    current_route = candidate_route
                    current_fitness = candidate_fitness
                    improvements = improvements + 1
                    improved = True
                    break

    return {
        "route": current_route,
        "fitness": current_fitness,
        "candidate_checks": candidate_checks,
        "improvements": improvements,
        "fitness_evaluations": fitness_evaluations,
    }


def are_edges_mutually_non_adjacent(edge_a, edge_b, edge_c, number_of_cities):
    edge_indexes = [edge_a, edge_b, edge_c]
    for first_index in range(3):
        for second_index in range(first_index + 1, 3):
            difference = abs(edge_indexes[first_index] - edge_indexes[second_index])
            if difference == 1 or difference == number_of_cities - 1:
                return False
    return True


def reverse_segment(segment):
    reversed_segment = segment.copy()
    reversed_segment.reverse()
    return reversed_segment


def build_three_opt_reconnections(route, first_edge, second_edge, third_edge):
    segment_a = route[third_edge + 1:] + route[:first_edge + 1]
    segment_b = route[first_edge + 1:second_edge + 1]
    segment_c = route[second_edge + 1:third_edge + 1]
    segments = [segment_a, segment_b, segment_c]
    reconnections = []

    for order in itertools.permutations([0, 1, 2]):
        for directions in itertools.product([False, True], repeat=3):
            candidate = []
            for position in range(3):
                segment = segments[order[position]]
                if directions[position]:
                    candidate = candidate + reverse_segment(segment)
                else:
                    candidate = candidate + segment
            reconnections.append(normalize_tour(candidate))

    return reconnections


def is_genuine_three_opt_candidate(original_route, candidate_route):
    original_edges = route_edges(original_route)
    candidate_edges = route_edges(candidate_route)
    removed_edges = original_edges - candidate_edges
    added_edges = candidate_edges - original_edges
    return len(removed_edges) >= 3 and len(added_edges) >= 3


def three_opt_first_improvement(route, distance_matrix):
    current_route = normalize_tour(route)
    current_fitness = tour_cost(current_route, distance_matrix)
    number_of_cities = len(current_route)
    edge_triples_checked = 0
    reconnections_checked = 0
    fitness_evaluations = 1

    for first_edge in range(number_of_cities):
        for second_edge in range(first_edge + 1, number_of_cities):
            for third_edge in range(second_edge + 1, number_of_cities):
                if not are_edges_mutually_non_adjacent(
                    first_edge,
                    second_edge,
                    third_edge,
                    number_of_cities,
                ):
                    continue

                edge_triples_checked = edge_triples_checked + 1
                seen_reconnections = set()
                reconnections = build_three_opt_reconnections(
                    current_route,
                    first_edge,
                    second_edge,
                    third_edge,
                )

                for candidate_route in reconnections:
                    candidate_key = tuple(candidate_route)
                    if candidate_key in seen_reconnections:
                        continue
                    seen_reconnections.add(candidate_key)

                    if candidate_route == current_route:
                        continue
                    if not is_valid_route(candidate_route, number_of_cities):
                        continue
                    if not is_genuine_three_opt_candidate(
                        current_route,
                        candidate_route,
                    ):
                        continue

                    reconnections_checked = reconnections_checked + 1
                    fitness_evaluations = fitness_evaluations + 1
                    candidate_fitness = tour_cost(candidate_route, distance_matrix)

                    if candidate_fitness < current_fitness:
                        return {
                            "route": candidate_route,
                            "fitness": candidate_fitness,
                            "edge_triples_checked": edge_triples_checked,
                            "reconnections_checked": reconnections_checked,
                            "improved": True,
                            "fitness_evaluations": fitness_evaluations,
                        }

    return {
        "route": current_route,
        "fitness": current_fitness,
        "edge_triples_checked": edge_triples_checked,
        "reconnections_checked": reconnections_checked,
        "improved": False,
        "fitness_evaluations": fitness_evaluations,
    }


def polish_with_two_opt_three_opt(route, distance_matrix):
    current_route = normalize_tour(route)
    two_opt_calls = 0
    two_opt_candidate_checks = 0
    two_opt_improvements = 0
    three_opt_calls = 0
    three_opt_edge_triples_checked = 0
    three_opt_reconnections_checked = 0
    three_opt_improvements = 0
    fitness_evaluations = 0

    while True:
        two_opt_calls = two_opt_calls + 1
        two_opt_result = two_opt_local_search(current_route, distance_matrix)
        two_opt_candidate_checks = (
            two_opt_candidate_checks + two_opt_result["candidate_checks"]
        )
        two_opt_improvements = two_opt_improvements + two_opt_result["improvements"]
        fitness_evaluations = (
            fitness_evaluations + two_opt_result["fitness_evaluations"]
        )
        current_route = two_opt_result["route"].copy()
        current_fitness = two_opt_result["fitness"]

        three_opt_calls = three_opt_calls + 1
        three_opt_result = three_opt_first_improvement(
            current_route,
            distance_matrix,
        )
        three_opt_edge_triples_checked = (
            three_opt_edge_triples_checked
            + three_opt_result["edge_triples_checked"]
        )
        three_opt_reconnections_checked = (
            three_opt_reconnections_checked
            + three_opt_result["reconnections_checked"]
        )
        fitness_evaluations = (
            fitness_evaluations + three_opt_result["fitness_evaluations"]
        )

        if not three_opt_result["improved"]:
            return {
                "route": current_route,
                "fitness": current_fitness,
                "two_opt_calls": two_opt_calls,
                "two_opt_candidate_checks": two_opt_candidate_checks,
                "two_opt_improvements": two_opt_improvements,
                "three_opt_calls": three_opt_calls,
                "three_opt_edge_triples_checked": three_opt_edge_triples_checked,
                "three_opt_reconnections_checked": three_opt_reconnections_checked,
                "three_opt_improvements": three_opt_improvements,
                "fitness_evaluations": fitness_evaluations,
            }

        three_opt_improvements = three_opt_improvements + 1
        current_route = three_opt_result["route"].copy()


def normal_round(value):
    return math.floor(value + 0.5)


def random_ana_value(rng):
    r = rng.uniform(-1.0, 1.0)
    while r == 0:
        r = rng.uniform(-1.0, 1.0)
    return r


def accept_with_sa(current_fitness, trial_fitness, temperature, rng, epsilon):
    if trial_fitness <= current_fitness:
        return True
    delta = trial_fitness - current_fitness
    delta_normalized = delta / (current_fitness + epsilon)
    probability = math.exp(-delta_normalized / temperature)
    u = rng.random()
    if u < probability:
        return True
    return False


def temperature_at(iteration, max_iterations, temperature_start, temperature_min):
    if max_iterations <= 1:
        return temperature_min
    progress = iteration / (max_iterations - 1)
    temperature = temperature_start + (temperature_min - temperature_start) * progress
    return temperature


def is_valid_route(route, number_of_cities):
    return sorted(route) == list(range(number_of_cities))


def create_initial_route(number_of_cities, rng):
    other_cities = []
    for city in range(1, number_of_cities):
        other_cities.append(city)
    rng.shuffle(other_cities)

    route = [0]
    for city in other_cities:
        route.append(city)
    return normalize_tour(route)


def move_ant(current, previous, best, current_fitness, previous_fitness,
             best_fitness, rho, rng, epsilon, memory_rank_cache, edge_memory,
             memory_edge_pairs, use_distance_weighted_memory,
             memory_candidate_pool_size, memory_max_edge_moves,
             memory_top_k_edges):
    number_of_cities = len(current)
    r = random_ana_value(rng)

    if current == best:
        M_A = max(1, math.ceil(rho * (number_of_cities - 1)))
        m = max(1, normal_round(abs(r) * M_A))
        trial = random_segment_inversion(current, m, rng)
        return trial, "case_a", None

    aligned_current = align_to_best(current, best)

    # Original ANA:
    # X_best - X_current
    #
    # TSP adaptation:
    # ordered swap sequence from current tour to best tour
    current_swaps = build_swap_sequence(aligned_current, best)
    if len(current_swaps) == 0:
        if current == previous:
            return current.copy(), "case_b", None
        return current.copy(), "general", None

    if current == previous:
        tau = 1
        dw = r
        alpha = abs(r)
        m = max(1, normal_round(alpha * len(current_swaps)))
        if dw > 0:
            memory_ranked_edges = ensure_memory_ranked_edges(
                memory_rank_cache,
                edge_memory,
                memory_edge_pairs,
                use_distance_weighted_memory,
                memory_candidate_pool_size,
            )
            memory_result = guide_by_memory_edges(
                current,
                memory_ranked_edges,
                dw,
                rng,
                memory_max_edge_moves,
                memory_top_k_edges,
            )
            trial = memory_result["route"]
        else:
            trial = random_segment_inversion(current, m, rng)
            memory_result = None
        return trial, "case_b", memory_result

    aligned_previous = align_to_best(previous, best)
    previous_swaps = build_swap_sequence(aligned_previous, best)

    s_current = len(current_swaps) / (number_of_cities - 1)
    s_previous = len(previous_swaps) / (number_of_cities - 1)

    q_current = max(0, current_fitness - best_fitness)
    q_current = q_current / (current_fitness + epsilon)
    q_previous = max(0, previous_fitness - best_fitness)
    q_previous = q_previous / (previous_fitness + epsilon)

    T_current = math.sqrt((s_current * s_current + q_current * q_current) / 2)
    T_previous = math.sqrt((s_previous * s_previous + q_previous * q_previous) / 2)
    tau = min(1, T_current / (T_previous + epsilon))
    dw = r * tau
    alpha = abs(dw)
    m = max(1, normal_round(alpha * len(current_swaps)))

    if dw > 0:
        memory_ranked_edges = ensure_memory_ranked_edges(
            memory_rank_cache,
            edge_memory,
            memory_edge_pairs,
            use_distance_weighted_memory,
            memory_candidate_pool_size,
        )
        memory_result = guide_by_memory_edges(
            current,
            memory_ranked_edges,
            dw,
            rng,
            memory_max_edge_moves,
            memory_top_k_edges,
        )
        trial = memory_result["route"]
    else:
        trial = random_segment_inversion(current, m, rng)
        memory_result = None
    return trial, "general", memory_result


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


def run_ana(coordinates, population_size, max_iterations, seed, rho,
            temperature_start, temperature_min, use_integer_distances=False,
            edge_memory_initial=1.0, edge_memory_evaporation_rate=0.02,
            edge_memory_max=10.0, global_best_deposit=1.0,
            near_best_deposit=0.3, near_best_gap=0.03,
            memory_max_edge_moves=3, memory_top_k_edges=20,
            use_distance_weighted_memory=True, memory_candidate_pool_size=100):
    epsilon = 0.000000000001
    rng = random.Random(seed)
    number_of_cities = len(coordinates)
    distance_matrix = build_distance_matrix(coordinates, use_integer_distances)
    memory_edge_pairs = precompute_memory_edge_pairs(distance_matrix)

    population = initialize_population(
        number_of_cities,
        population_size,
        distance_matrix,
        rng,
    )
    routes = population[0]
    previous_routes = population[1]
    fitnesses = population[2]
    previous_fitnesses = population[3]
    best_route, best_fitness = find_best_route(routes, fitnesses)
    edge_memory = initialize_edge_memory(number_of_cities, edge_memory_initial)

    history = [best_fitness]
    accepted_worse = 0
    rejected_worse = 0
    case_a_count = 0
    case_b_count = 0
    general_count = 0
    three_opt_calls = 0
    three_opt_edge_triples_checked = 0
    three_opt_reconnections_checked = 0
    three_opt_improvements = 0
    two_opt_calls = 0
    two_opt_candidate_checks = 0
    two_opt_improvements = 0
    total_fitness_evaluations = population_size
    edge_memory_deposits = 0
    edge_memory_evaporations = 0
    memory_guided_moves = 0
    memory_selected_edges = 0
    memory_inserted_edges = 0
    memory_failed_insertions = 0
    memory_near_best_deposits = 0
    memory_global_best_deposits = 0
    selected_edge_memory_total = 0.0
    selected_edge_distance_total = 0.0
    memory_rank_cache = {
        "ranked_edges": [],
        "dirty": True,
        "rebuilds": 0,
        "dirty_rebuilds": 0,
        "pool_size_total": 0,
    }
    memory_selection_random_choices = 0
    memory_selection_greedy_choices = 0

    edge_memory_deposits = edge_memory_deposits + deposit_route_edges(
        edge_memory,
        best_route,
        global_best_deposit,
        edge_memory_max,
    )
    memory_global_best_deposits = memory_global_best_deposits + 1
    memory_rank_cache["dirty"] = True

    for iteration in range(max_iterations):
        edge_memory_evaporations = (
            edge_memory_evaporations
            + evaporate_edge_memory(
                edge_memory,
                edge_memory_evaporation_rate,
                edge_memory_max,
            )
        )
        memory_rank_cache["dirty"] = True
        edge_memory_deposits = edge_memory_deposits + deposit_route_edges(
            edge_memory,
            best_route,
            global_best_deposit,
            edge_memory_max,
        )
        memory_global_best_deposits = memory_global_best_deposits + 1
        memory_rank_cache["dirty"] = True
        temperature = temperature_at(
            iteration,
            max_iterations,
            temperature_start,
            temperature_min,
        )

        for i in range(population_size):
            current = routes[i]
            previous = previous_routes[i]
            current_fitness = fitnesses[i]
            previous_fitness = previous_fitnesses[i]
            trial, case_name, memory_result = move_ant(
                current,
                previous,
                best_route,
                current_fitness,
                previous_fitness,
                best_fitness,
                rho,
                rng,
                epsilon,
                memory_rank_cache,
                edge_memory,
                memory_edge_pairs,
                use_distance_weighted_memory,
                memory_candidate_pool_size,
                memory_max_edge_moves,
                memory_top_k_edges,
            )

            if memory_result is not None:
                memory_guided_moves = memory_guided_moves + 1
                memory_selected_edges = (
                    memory_selected_edges + memory_result["selected_edges"]
                )
                memory_inserted_edges = (
                    memory_inserted_edges + memory_result["inserted_edges"]
                )
                memory_failed_insertions = (
                    memory_failed_insertions
                    + memory_result["failed_insertions"]
                )
                selected_edge_memory_total = (
                    selected_edge_memory_total
                    + memory_result["selected_memory_total"]
                )
                selected_edge_distance_total = (
                    selected_edge_distance_total
                    + memory_result["selected_distance_total"]
                )
                memory_selection_random_choices = (
                    memory_selection_random_choices
                    + memory_result["selected_edges"]
                )

            if case_name == "case_a":
                case_a_count = case_a_count + 1
            elif case_name == "case_b":
                case_b_count = case_b_count + 1
            else:
                general_count = general_count + 1

            trial = normalize_tour(trial)
            if not is_valid_route(trial, number_of_cities):
                print("Error: invalid route")
                return

            trial_fitness = tour_cost(trial, distance_matrix)
            total_fitness_evaluations = total_fitness_evaluations + 1
            accepted = accept_with_sa(
                current_fitness,
                trial_fitness,
                temperature,
                rng,
                epsilon,
            )

            if accepted:
                if trial_fitness > current_fitness:
                    accepted_worse = accepted_worse + 1
                if trial_fitness <= best_fitness * (1.0 + near_best_gap):
                    edge_memory_deposits = (
                        edge_memory_deposits
                        + deposit_route_edges(
                            edge_memory,
                            trial,
                            near_best_deposit,
                            edge_memory_max,
                        )
                    )
                    memory_near_best_deposits = memory_near_best_deposits + 1
                    memory_rank_cache["dirty"] = True
                previous_routes[i] = routes[i].copy()
                previous_fitnesses[i] = fitnesses[i]
                if trial_fitness < best_fitness:
                    polish_result = polish_with_two_opt_three_opt(
                        trial,
                        distance_matrix,
                    )
                    three_opt_calls = (
                        three_opt_calls + polish_result["three_opt_calls"]
                    )
                    three_opt_edge_triples_checked = (
                        three_opt_edge_triples_checked
                        + polish_result["three_opt_edge_triples_checked"]
                    )
                    three_opt_reconnections_checked = (
                        three_opt_reconnections_checked
                        + polish_result["three_opt_reconnections_checked"]
                    )
                    three_opt_improvements = (
                        three_opt_improvements
                        + polish_result["three_opt_improvements"]
                    )
                    two_opt_calls = two_opt_calls + polish_result["two_opt_calls"]
                    two_opt_candidate_checks = (
                        two_opt_candidate_checks
                        + polish_result["two_opt_candidate_checks"]
                    )
                    two_opt_improvements = (
                        two_opt_improvements
                        + polish_result["two_opt_improvements"]
                    )
                    total_fitness_evaluations = (
                        total_fitness_evaluations
                        + polish_result["fitness_evaluations"]
                    )
                    if not is_valid_route(polish_result["route"], number_of_cities):
                        print("Error: invalid polished route")
                        return
                    routes[i] = polish_result["route"].copy()
                    fitnesses[i] = polish_result["fitness"]
                    best_route = polish_result["route"].copy()
                    best_fitness = polish_result["fitness"]
                    edge_memory_deposits = (
                        edge_memory_deposits
                        + deposit_route_edges(
                            edge_memory,
                            best_route,
                            global_best_deposit,
                            edge_memory_max,
                        )
                    )
                    memory_global_best_deposits = memory_global_best_deposits + 1
                    memory_rank_cache["dirty"] = True
                else:
                    routes[i] = trial.copy()
                    fitnesses[i] = trial_fitness
            else:
                if trial_fitness > current_fitness:
                    rejected_worse = rejected_worse + 1

        history.append(best_fitness)

    mean_selected_edge_memory = 0.0
    mean_selected_edge_distance = 0.0
    if memory_selected_edges > 0:
        mean_selected_edge_memory = (
            selected_edge_memory_total / memory_selected_edges
        )
        mean_selected_edge_distance = (
            selected_edge_distance_total / memory_selected_edges
        )
    mean_memory_ranked_pool_size = 0.0
    memory_ranked_pool_rebuilds = memory_rank_cache["rebuilds"]
    if memory_ranked_pool_rebuilds > 0:
        mean_memory_ranked_pool_size = (
            memory_rank_cache["pool_size_total"] / memory_ranked_pool_rebuilds
        )
    memory_pair_scans_saved_estimate = (
        memory_selected_edges * len(memory_edge_pairs)
        - memory_ranked_pool_rebuilds * len(memory_edge_pairs)
    )
    if memory_pair_scans_saved_estimate < 0:
        memory_pair_scans_saved_estimate = 0

    return {
        "best_route": best_route,
        "best_fitness": best_fitness,
        "history": history,
        "accepted_worse": accepted_worse,
        "rejected_worse": rejected_worse,
        "case_a": case_a_count,
        "case_b": case_b_count,
        "general": general_count,
        "three_opt_calls": three_opt_calls,
        "three_opt_edge_triples_checked": three_opt_edge_triples_checked,
        "three_opt_reconnections_checked": three_opt_reconnections_checked,
        "three_opt_improvements": three_opt_improvements,
        "two_opt_calls": two_opt_calls,
        "two_opt_candidate_checks": two_opt_candidate_checks,
        "two_opt_improvements": two_opt_improvements,
        "total_fitness_evaluations": total_fitness_evaluations,
        "edge_memory_deposits": edge_memory_deposits,
        "edge_memory_evaporations": edge_memory_evaporations,
        "memory_guided_moves": memory_guided_moves,
        "memory_selected_edges": memory_selected_edges,
        "memory_inserted_edges": memory_inserted_edges,
        "memory_failed_insertions": memory_failed_insertions,
        "memory_near_best_deposits": memory_near_best_deposits,
        "memory_global_best_deposits": memory_global_best_deposits,
        "mean_selected_edge_memory": mean_selected_edge_memory,
        "mean_selected_edge_distance": mean_selected_edge_distance,
        "memory_ranked_pool_rebuilds": memory_ranked_pool_rebuilds,
        "memory_ranked_pool_size": mean_memory_ranked_pool_size,
        "memory_pair_scans_saved_estimate": memory_pair_scans_saved_estimate,
        "memory_dirty_rebuilds": memory_rank_cache["dirty_rebuilds"],
        "memory_selection_random_choices": memory_selection_random_choices,
        "memory_selection_greedy_choices": memory_selection_greedy_choices,
    }
