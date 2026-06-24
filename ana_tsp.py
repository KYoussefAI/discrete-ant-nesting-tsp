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
        trial = random_swaps(current, m, rng)
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
            trial = apply_first_swaps(aligned_current, current_swaps, m)
        else:
            trial = random_swaps(current, m, rng)
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
        trial = apply_first_swaps(aligned_current, current_swaps, m)
    else:
        trial = random_swaps(current, m, rng)
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
            temperature_start, temperature_min, use_integer_distances=False):
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
                routes[i] = trial.copy()
                fitnesses[i] = trial_fitness
                if trial_fitness < best_fitness:
                    best_route = trial.copy()
                    best_fitness = trial_fitness
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
    }
