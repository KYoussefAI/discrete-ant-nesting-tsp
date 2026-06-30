import math
import random


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
            temperature_start, temperature_min,
            two_opt_trigger_temperature_start,
            two_opt_trigger_temperature_min,
            use_integer_distances=False):
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
    two_opt_calls = 0
    two_opt_trigger_attempts = 0
    two_opt_trigger_accepted = 0
    two_opt_trigger_rejected = 0
    two_opt_forced_calls = 0
    two_opt_probabilistic_calls = 0
    two_opt_candidate_checks = 0
    two_opt_improvements = 0
    total_fitness_evaluations = population_size
    optimized_routes = set()

    for iteration in range(max_iterations):
        temperature = temperature_at(
            iteration,
            max_iterations,
            temperature_start,
            temperature_min,
        )
        two_opt_trigger_temperature = temperature_at(
            iteration,
            max_iterations,
            two_opt_trigger_temperature_start,
            two_opt_trigger_temperature_min,
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
                launch_two_opt = False
                if trial_fitness < best_fitness:
                    launch_two_opt = True
                    two_opt_forced_calls = two_opt_forced_calls + 1
                else:
                    trial_key = tuple(trial)
                    relative_gap = (
                        trial_fitness - best_fitness
                    ) / best_fitness
                    edge_difference = (
                        len(missing_best_edges(trial, best_route))
                        / number_of_cities
                    )
                    if (
                        relative_gap > 0
                        and relative_gap <= 0.01
                        and edge_difference >= 0.20
                        and trial_key not in optimized_routes
                    ):
                        two_opt_trigger_attempts = two_opt_trigger_attempts + 1
                        max_trigger_probability = 0.05
                        launch_probability = max_trigger_probability * math.exp(
                            -relative_gap / two_opt_trigger_temperature
                        )
                        if rng.random() < launch_probability:
                            launch_two_opt = True
                            two_opt_trigger_accepted = two_opt_trigger_accepted + 1
                            two_opt_probabilistic_calls = (
                                two_opt_probabilistic_calls + 1
                            )
                        else:
                            two_opt_trigger_rejected = two_opt_trigger_rejected + 1

                if launch_two_opt:
                    optimized_routes.add(tuple(trial))
                    two_opt_calls = two_opt_calls + 1
                    two_opt_result = two_opt_local_search(trial, distance_matrix)
                    two_opt_candidate_checks = (
                        two_opt_candidate_checks
                        + two_opt_result["candidate_checks"]
                    )
                    two_opt_improvements = (
                        two_opt_improvements
                        + two_opt_result["improvements"]
                    )
                    total_fitness_evaluations = (
                        total_fitness_evaluations
                        + two_opt_result["fitness_evaluations"]
                    )
                    if not is_valid_route(two_opt_result["route"], number_of_cities):
                        print("Error: invalid 2-opt route")
                        return
                    routes[i] = two_opt_result["route"].copy()
                    fitnesses[i] = two_opt_result["fitness"]
                    if two_opt_result["fitness"] < best_fitness:
                        best_route = two_opt_result["route"].copy()
                        best_fitness = two_opt_result["fitness"]
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
        "two_opt_calls": two_opt_calls,
        "two_opt_trigger_attempts": two_opt_trigger_attempts,
        "two_opt_trigger_accepted": two_opt_trigger_accepted,
        "two_opt_trigger_rejected": two_opt_trigger_rejected,
        "two_opt_forced_calls": two_opt_forced_calls,
        "two_opt_probabilistic_calls": two_opt_probabilistic_calls,
        "two_opt_candidate_checks": two_opt_candidate_checks,
        "two_opt_improvements": two_opt_improvements,
        "total_fitness_evaluations": total_fitness_evaluations,
    }
