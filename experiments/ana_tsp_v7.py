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


def make_tabu_stats():
    return {
        "tabu_calls": 0,
        "tabu_steps": 0,
        "tabu_candidate_checks": 0,
        "tabu_admissible_moves": 0,
        "tabu_moves_accepted": 0,
        "tabu_improving_moves": 0,
        "tabu_worse_moves": 0,
        "tabu_aspiration_overrides": 0,
        "tabu_best_improvements": 0,
        "tabu_final_route_polish_calls": 0,
        "tabu_final_route_polish_improvements": 0,
        "tabu_best_route_polish_improvements": 0,
        "tabu_stops_max_steps": 0,
        "tabu_stops_no_improvement": 0,
        "tabu_stops_no_admissible_move": 0,
    }


def add_tabu_stats(total_stats, call_stats):
    for key in total_stats:
        total_stats[key] = total_stats[key] + call_stats[key]


def valid_two_opt_moves(number_of_cities):
    moves = []
    for start_index in range(1, number_of_cities - 1):
        for end_index in range(start_index + 1, number_of_cities):
            if start_index == 1 and end_index == number_of_cities - 1:
                continue
            moves.append((start_index, end_index))
    return moves


def two_opt_move_edges(route, start_index, end_index):
    before_start = route[start_index - 1]
    segment_start = route[start_index]
    segment_end = route[end_index]
    after_end = route[(end_index + 1) % len(route)]

    removed_edges = (
        make_edge(before_start, segment_start),
        make_edge(segment_end, after_end),
    )
    added_edges = (
        make_edge(before_start, segment_end),
        make_edge(segment_start, after_end),
    )
    return removed_edges, added_edges


def apply_two_opt_move(route, start_index, end_index):
    candidate_route = route.copy()
    candidate_route[start_index:end_index + 1] = reversed(
        candidate_route[start_index:end_index + 1]
    )
    return normalize_tour(candidate_route)


def choose_tabu_candidate_moves(number_of_cities, sample_size, rng):
    moves = valid_two_opt_moves(number_of_cities)
    if sample_size is None or sample_size >= len(moves):
        return moves
    return rng.sample(moves, sample_size)


def tabu_move_allowed(added_edges, tabu_until, current_tabu_step,
                      candidate_fitness, best_tabu_fitness,
                      global_best_fitness):
    move_is_tabu = False
    for edge in added_edges:
        if edge in tabu_until and tabu_until[edge] > current_tabu_step:
            move_is_tabu = True
            break

    if not move_is_tabu:
        return True, False

    if candidate_fitness < best_tabu_fitness:
        return True, True
    if candidate_fitness < global_best_fitness:
        return True, True

    return False, False


def tabu_search(
    route,
    fitness,
    distance_matrix,
    global_best_fitness,
    tabu_tenure,
    tabu_max_steps,
    tabu_no_improvement_limit,
    tabu_candidate_sample_size,
    rng,
):
    current_route = normalize_tour(route)
    current_fitness = fitness
    best_tabu_route = current_route.copy()
    best_tabu_fitness = current_fitness
    tabu_until = {}
    stats = make_tabu_stats()
    stats["tabu_calls"] = 1
    no_improvement_steps = 0
    stop_reason = "max_steps"

    for tabu_step in range(tabu_max_steps):
        best_candidate = None
        best_candidate_fitness = None
        best_removed_edges = None
        best_move_was_tabu = False

        candidate_moves = choose_tabu_candidate_moves(
            len(current_route),
            tabu_candidate_sample_size,
            rng,
        )

        for start_index, end_index in candidate_moves:
            stats["tabu_candidate_checks"] = stats["tabu_candidate_checks"] + 1
            removed_edges, added_edges = two_opt_move_edges(
                current_route,
                start_index,
                end_index,
            )

            candidate_route = apply_two_opt_move(
                current_route,
                start_index,
                end_index,
            )
            candidate_fitness = tour_cost(candidate_route, distance_matrix)
            allowed, aspiration = tabu_move_allowed(
                added_edges,
                tabu_until,
                tabu_step,
                candidate_fitness,
                best_tabu_fitness,
                global_best_fitness,
            )

            if not allowed:
                continue

            stats["tabu_admissible_moves"] = (
                stats["tabu_admissible_moves"] + 1
            )

            if (
                best_candidate is None
                or candidate_fitness < best_candidate_fitness
            ):
                best_candidate = candidate_route
                best_candidate_fitness = candidate_fitness
                best_removed_edges = removed_edges
                best_move_was_tabu = aspiration

        if best_candidate is None:
            stop_reason = "no_admissible_move"
            break

        if best_move_was_tabu:
            stats["tabu_aspiration_overrides"] = (
                stats["tabu_aspiration_overrides"] + 1
            )

        if best_candidate_fitness < current_fitness:
            stats["tabu_improving_moves"] = stats["tabu_improving_moves"] + 1
        else:
            stats["tabu_worse_moves"] = stats["tabu_worse_moves"] + 1

        current_route = best_candidate
        current_fitness = best_candidate_fitness
        stats["tabu_steps"] = stats["tabu_steps"] + 1
        stats["tabu_moves_accepted"] = stats["tabu_moves_accepted"] + 1

        for edge in best_removed_edges:
            tabu_until[edge] = tabu_step + tabu_tenure

        if current_fitness < best_tabu_fitness:
            best_tabu_route = current_route.copy()
            best_tabu_fitness = current_fitness
            stats["tabu_best_improvements"] = (
                stats["tabu_best_improvements"] + 1
            )
            no_improvement_steps = 0
        else:
            no_improvement_steps = no_improvement_steps + 1

        if no_improvement_steps >= tabu_no_improvement_limit:
            stop_reason = "no_improvement"
            break

    if stop_reason == "max_steps":
        stats["tabu_stops_max_steps"] = 1
    elif stop_reason == "no_improvement":
        stats["tabu_stops_no_improvement"] = 1
    else:
        stats["tabu_stops_no_admissible_move"] = 1

    return {
        "best_route": best_tabu_route,
        "best_fitness": best_tabu_fitness,
        "final_route": current_route,
        "final_fitness": current_fitness,
        "stats": stats,
    }


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
             best_fitness, rho, rng, epsilon):
    number_of_cities = len(current)
    r = random_ana_value(rng)

    if current == best:
        M_A = max(1, math.ceil(rho * (number_of_cities - 1)))
        m = max(1, normal_round(abs(r) * M_A))
        trial = random_segment_inversion(current, m, rng)
        return trial, "case_a"

    aligned_current = align_to_best(current, best)

    # Original ANA:
    # X_best - X_current
    #
    # TSP adaptation:
    # ordered swap sequence from current tour to best tour
    current_swaps = build_swap_sequence(aligned_current, best)
    if len(current_swaps) == 0:
        if current == previous:
            return current.copy(), "case_b"
        return current.copy(), "general"

    if current == previous:
        tau = 1
        dw = r
        alpha = abs(r)
        m = max(1, normal_round(alpha * len(current_swaps)))
        if dw > 0:
            trial = guide_by_best_edges(current, best, m, rng)
        else:
            trial = random_segment_inversion(current, m, rng)
        return trial, "case_b"

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
        trial = guide_by_best_edges(current, best, m, rng)
    else:
        trial = random_segment_inversion(current, m, rng)
    return trial, "general"


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
            tabu_tenure=7, tabu_max_steps=50,
            tabu_no_improvement_limit=20, tabu_candidate_sample_size=None):
    epsilon = 0.000000000001
    rng = random.Random(seed)
    number_of_cities = len(coordinates)
    distance_matrix = build_distance_matrix(coordinates, use_integer_distances)

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
    tabu_stats = make_tabu_stats()
    total_fitness_evaluations = population_size

    for iteration in range(max_iterations):
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
            trial, case_name = move_ant(
                current,
                previous,
                best_route,
                current_fitness,
                previous_fitness,
                best_fitness,
                rho,
                rng,
                epsilon,
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

                    tabu_result = tabu_search(
                        polish_result["route"],
                        polish_result["fitness"],
                        distance_matrix,
                        best_fitness,
                        tabu_tenure,
                        tabu_max_steps,
                        tabu_no_improvement_limit,
                        tabu_candidate_sample_size,
                        rng,
                    )
                    add_tabu_stats(tabu_stats, tabu_result["stats"])
                    total_fitness_evaluations = (
                        total_fitness_evaluations
                        + tabu_result["stats"]["tabu_candidate_checks"]
                    )
                    if not is_valid_route(
                        tabu_result["best_route"],
                        number_of_cities,
                    ):
                        print("Error: invalid best tabu route")
                        return
                    if not is_valid_route(
                        tabu_result["final_route"],
                        number_of_cities,
                    ):
                        print("Error: invalid final tabu route")
                        return

                    polished_best_tabu = polish_with_two_opt_three_opt(
                        tabu_result["best_route"],
                        distance_matrix,
                    )
                    tabu_stats["tabu_best_route_polish_improvements"] = (
                        tabu_stats["tabu_best_route_polish_improvements"]
                        + polished_best_tabu["two_opt_improvements"]
                        + polished_best_tabu["three_opt_improvements"]
                    )
                    three_opt_calls = (
                        three_opt_calls + polished_best_tabu["three_opt_calls"]
                    )
                    three_opt_edge_triples_checked = (
                        three_opt_edge_triples_checked
                        + polished_best_tabu["three_opt_edge_triples_checked"]
                    )
                    three_opt_reconnections_checked = (
                        three_opt_reconnections_checked
                        + polished_best_tabu["three_opt_reconnections_checked"]
                    )
                    three_opt_improvements = (
                        three_opt_improvements
                        + polished_best_tabu["three_opt_improvements"]
                    )
                    two_opt_calls = (
                        two_opt_calls + polished_best_tabu["two_opt_calls"]
                    )
                    two_opt_candidate_checks = (
                        two_opt_candidate_checks
                        + polished_best_tabu["two_opt_candidate_checks"]
                    )
                    two_opt_improvements = (
                        two_opt_improvements
                        + polished_best_tabu["two_opt_improvements"]
                    )
                    total_fitness_evaluations = (
                        total_fitness_evaluations
                        + polished_best_tabu["fitness_evaluations"]
                    )
                    if not is_valid_route(
                        polished_best_tabu["route"],
                        number_of_cities,
                    ):
                        print("Error: invalid polished best tabu route")
                        return

                    polished_final_tabu = polish_with_two_opt_three_opt(
                        tabu_result["final_route"],
                        distance_matrix,
                    )
                    tabu_stats["tabu_final_route_polish_calls"] = (
                        tabu_stats["tabu_final_route_polish_calls"] + 1
                    )
                    tabu_stats["tabu_final_route_polish_improvements"] = (
                        tabu_stats["tabu_final_route_polish_improvements"]
                        + polished_final_tabu["two_opt_improvements"]
                        + polished_final_tabu["three_opt_improvements"]
                    )
                    three_opt_calls = (
                        three_opt_calls + polished_final_tabu["three_opt_calls"]
                    )
                    three_opt_edge_triples_checked = (
                        three_opt_edge_triples_checked
                        + polished_final_tabu["three_opt_edge_triples_checked"]
                    )
                    three_opt_reconnections_checked = (
                        three_opt_reconnections_checked
                        + polished_final_tabu["three_opt_reconnections_checked"]
                    )
                    three_opt_improvements = (
                        three_opt_improvements
                        + polished_final_tabu["three_opt_improvements"]
                    )
                    two_opt_calls = (
                        two_opt_calls + polished_final_tabu["two_opt_calls"]
                    )
                    two_opt_candidate_checks = (
                        two_opt_candidate_checks
                        + polished_final_tabu["two_opt_candidate_checks"]
                    )
                    two_opt_improvements = (
                        two_opt_improvements
                        + polished_final_tabu["two_opt_improvements"]
                    )
                    total_fitness_evaluations = (
                        total_fitness_evaluations
                        + polished_final_tabu["fitness_evaluations"]
                    )
                    if not is_valid_route(
                        polished_final_tabu["route"],
                        number_of_cities,
                    ):
                        print("Error: invalid polished final tabu route")
                        return

                    final_result = polish_result
                    if polished_best_tabu["fitness"] < final_result["fitness"]:
                        final_result = polished_best_tabu
                    if polished_final_tabu["fitness"] < final_result["fitness"]:
                        final_result = polished_final_tabu

                    routes[i] = final_result["route"].copy()
                    fitnesses[i] = final_result["fitness"]
                    best_route = final_result["route"].copy()
                    best_fitness = final_result["fitness"]
                else:
                    routes[i] = trial.copy()
                    fitnesses[i] = trial_fitness
            else:
                if trial_fitness > current_fitness:
                    rejected_worse = rejected_worse + 1

        history.append(best_fitness)

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
        "tabu_calls": tabu_stats["tabu_calls"],
        "tabu_steps": tabu_stats["tabu_steps"],
        "tabu_candidate_checks": tabu_stats["tabu_candidate_checks"],
        "tabu_admissible_moves": tabu_stats["tabu_admissible_moves"],
        "tabu_moves_accepted": tabu_stats["tabu_moves_accepted"],
        "tabu_improving_moves": tabu_stats["tabu_improving_moves"],
        "tabu_worse_moves": tabu_stats["tabu_worse_moves"],
        "tabu_aspiration_overrides": tabu_stats["tabu_aspiration_overrides"],
        "tabu_best_improvements": tabu_stats["tabu_best_improvements"],
        "tabu_final_route_polish_calls": (
            tabu_stats["tabu_final_route_polish_calls"]
        ),
        "tabu_final_route_polish_improvements": (
            tabu_stats["tabu_final_route_polish_improvements"]
        ),
        "tabu_best_route_polish_improvements": (
            tabu_stats["tabu_best_route_polish_improvements"]
        ),
        "tabu_stops_max_steps": tabu_stats["tabu_stops_max_steps"],
        "tabu_stops_no_improvement": tabu_stats["tabu_stops_no_improvement"],
        "tabu_stops_no_admissible_move": (
            tabu_stats["tabu_stops_no_admissible_move"]
        ),
        "total_fitness_evaluations": total_fitness_evaluations,
    }
