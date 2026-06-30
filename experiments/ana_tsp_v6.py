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


def shared_edge_ratio(route_a, route_b):
    edges_a = route_edges(normalize_tour(route_a))
    edges_b = route_edges(normalize_tour(route_b))
    return len(edges_a.intersection(edges_b)) / len(edges_a)


def edge_diversity(route_a, route_b):
    return 1.0 - shared_edge_ratio(route_a, route_b)


def make_archive_entry(route, fitness):
    return {
        "route": normalize_tour(route),
        "fitness": fitness,
        "edges": route_edges(route),
    }


def make_archive_stats():
    return {
        "insert_attempts": 0,
        "insertions": 0,
        "replacements": 0,
        "rejected_similar": 0,
        "rejected_quality": 0,
    }


def is_diverse_enough(route, archive, minimum_edge_diversity):
    if len(archive) == 0:
        return True

    for entry in archive:
        if edge_diversity(route, entry["route"]) < minimum_edge_diversity:
            return False

    return True


def add_route_to_archive(route, fitness, archive, archive_size,
                         minimum_edge_diversity, archive_stats=None):
    if archive_stats is not None:
        archive_stats["insert_attempts"] = archive_stats["insert_attempts"] + 1

    normalized_route = normalize_tour(route)

    for index, entry in enumerate(archive):
        if entry["route"] == normalized_route:
            if fitness < entry["fitness"]:
                archive[index] = make_archive_entry(normalized_route, fitness)
                archive.sort(key=lambda item: item["fitness"])
                if archive_stats is not None:
                    archive_stats["replacements"] = (
                        archive_stats["replacements"] + 1
                    )
                return "replacement"
            if archive_stats is not None:
                archive_stats["rejected_quality"] = (
                    archive_stats["rejected_quality"] + 1
                )
            return "rejected_quality"

    if is_diverse_enough(normalized_route, archive, minimum_edge_diversity):
        if len(archive) < archive_size:
            archive.append(make_archive_entry(normalized_route, fitness))
            archive.sort(key=lambda item: item["fitness"])
            if archive_stats is not None:
                archive_stats["insertions"] = archive_stats["insertions"] + 1
            return "insertion"

        worst_index = len(archive) - 1
        if fitness < archive[worst_index]["fitness"]:
            archive[worst_index] = make_archive_entry(normalized_route, fitness)
            archive.sort(key=lambda item: item["fitness"])
            if archive_stats is not None:
                archive_stats["replacements"] = (
                    archive_stats["replacements"] + 1
                )
            return "replacement"

        if archive_stats is not None:
            archive_stats["rejected_quality"] = (
                archive_stats["rejected_quality"] + 1
            )
        return "rejected_quality"

    closest_index = None
    closest_overlap = -1.0
    for index, entry in enumerate(archive):
        overlap = shared_edge_ratio(normalized_route, entry["route"])
        if overlap > closest_overlap:
            closest_overlap = overlap
            closest_index = index

    if closest_index is not None and fitness < archive[closest_index]["fitness"]:
        archive[closest_index] = make_archive_entry(normalized_route, fitness)
        archive.sort(key=lambda item: item["fitness"])
        if archive_stats is not None:
            archive_stats["replacements"] = archive_stats["replacements"] + 1
        return "replacement"

    if archive_stats is not None:
        archive_stats["rejected_similar"] = archive_stats["rejected_similar"] + 1
    return "rejected_similar"


def initialize_archive(routes, fitnesses, archive_size, minimum_edge_diversity,
                       archive_stats=None):
    archive = []
    indexes = list(range(len(routes)))
    indexes.sort(key=lambda index: fitnesses[index])

    for index in indexes:
        add_route_to_archive(
            routes[index],
            fitnesses[index],
            archive,
            archive_size,
            minimum_edge_diversity,
            archive_stats,
        )

    return archive


def choose_archive_teacher(archive, rng):
    if len(archive) == 0:
        return None

    elite_limit = min(3, len(archive))
    return archive[rng.randrange(elite_limit)]["route"]


def mean_archive_edge_diversity(archive):
    if len(archive) < 2:
        return 0.0

    diversity_sum = 0.0
    comparisons = 0

    for first_index in range(len(archive)):
        for second_index in range(first_index + 1, len(archive)):
            diversity_sum = diversity_sum + edge_diversity(
                archive[first_index]["route"],
                archive[second_index]["route"],
            )
            comparisons = comparisons + 1

    return diversity_sum / comparisons


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


def empty_three_opt_stats(route, fitness):
    return {
        "route": route,
        "fitness": fitness,
        "two_opt_calls": 0,
        "two_opt_candidate_checks": 0,
        "two_opt_improvements": 0,
        "three_opt_calls": 0,
        "three_opt_edge_triples_checked": 0,
        "three_opt_reconnections_checked": 0,
        "three_opt_improvements": 0,
        "fitness_evaluations": 0,
    }


def polish_with_two_opt_only(route, distance_matrix):
    two_opt_result = two_opt_local_search(route, distance_matrix)
    return {
        "route": two_opt_result["route"],
        "fitness": two_opt_result["fitness"],
        "two_opt_calls": 1,
        "two_opt_candidate_checks": two_opt_result["candidate_checks"],
        "two_opt_improvements": two_opt_result["improvements"],
        "three_opt_calls": 0,
        "three_opt_edge_triples_checked": 0,
        "three_opt_reconnections_checked": 0,
        "three_opt_improvements": 0,
        "fitness_evaluations": two_opt_result["fitness_evaluations"],
    }


def polish_route(route, fitness, distance_matrix, local_search_mode):
    if local_search_mode == "none":
        return empty_three_opt_stats(route, fitness)
    if local_search_mode == "2opt":
        return polish_with_two_opt_only(route, distance_matrix)
    return polish_with_two_opt_three_opt(route, distance_matrix)


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


def choose_teacher_for_positive_move(archive, best, rng):
    teacher = choose_archive_teacher(archive, rng)
    if teacher is None or teacher == best:
        return best, "global_best"
    return teacher, "archive"


def move_ant(current, previous, best, archive, current_fitness, previous_fitness,
             best_fitness, rho, rng, epsilon):
    number_of_cities = len(current)
    r = random_ana_value(rng)

    if current == best:
        M_A = max(1, math.ceil(rho * (number_of_cities - 1)))
        m = max(1, normal_round(abs(r) * M_A))
        trial = random_segment_inversion(current, m, rng)
        return trial, "case_a", "none"

    aligned_current = align_to_best(current, best)

    # Original ANA:
    # X_best - X_current
    #
    # TSP adaptation:
    # ordered swap sequence from current tour to best tour
    current_swaps = build_swap_sequence(aligned_current, best)
    if len(current_swaps) == 0:
        if current == previous:
            return current.copy(), "case_b", "none"
        return current.copy(), "general", "none"

    if current == previous:
        tau = 1
        dw = r
        alpha = abs(r)
        m = max(1, normal_round(alpha * len(current_swaps)))
        if dw > 0:
            teacher, teacher_source = choose_teacher_for_positive_move(
                archive,
                best,
                rng,
            )
            trial = guide_by_best_edges(current, teacher, m, rng)
            return trial, "case_b", teacher_source
        else:
            trial = random_segment_inversion(current, m, rng)
            return trial, "case_b", "none"

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
        teacher, teacher_source = choose_teacher_for_positive_move(
            archive,
            best,
            rng,
        )
        trial = guide_by_best_edges(current, teacher, m, rng)
        return trial, "general", teacher_source
    else:
        trial = random_segment_inversion(current, m, rng)
        return trial, "general", "none"


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
            archive_size=5, archive_min_edge_diversity=0.25,
            archive_near_best_gap=0.05, local_search_mode="2opt_3opt"):
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
    archive_stats = make_archive_stats()
    archive = initialize_archive(
        routes,
        fitnesses,
        archive_size,
        archive_min_edge_diversity,
        archive_stats,
    )

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
    teacher_global_best_choices = 0
    teacher_archive_choices = 0
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
            trial, case_name, teacher_source = move_ant(
                current,
                previous,
                best_route,
                archive,
                current_fitness,
                previous_fitness,
                best_fitness,
                rho,
                rng,
                epsilon,
            )
            if teacher_source == "global_best":
                teacher_global_best_choices = teacher_global_best_choices + 1
            elif teacher_source == "archive":
                teacher_archive_choices = teacher_archive_choices + 1

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
                    polish_result = polish_route(
                        trial,
                        trial_fitness,
                        distance_matrix,
                        local_search_mode,
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
                    add_route_to_archive(
                        best_route,
                        best_fitness,
                        archive,
                        archive_size,
                        archive_min_edge_diversity,
                        archive_stats,
                    )
                else:
                    routes[i] = trial.copy()
                    fitnesses[i] = trial_fitness
                    near_best_limit = best_fitness * (1 + archive_near_best_gap)
                    if trial_fitness <= near_best_limit:
                        add_route_to_archive(
                            trial,
                            trial_fitness,
                            archive,
                            archive_size,
                            archive_min_edge_diversity,
                            archive_stats,
                        )
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
        "archive_insert_attempts": archive_stats["insert_attempts"],
        "archive_insertions": archive_stats["insertions"],
        "archive_replacements": archive_stats["replacements"],
        "archive_rejected_similar": archive_stats["rejected_similar"],
        "archive_rejected_quality": archive_stats["rejected_quality"],
        "archive_final_size": len(archive),
        "teacher_global_best_choices": teacher_global_best_choices,
        "teacher_archive_choices": teacher_archive_choices,
        "mean_archive_edge_diversity": mean_archive_edge_diversity(archive),
        "total_fitness_evaluations": total_fitness_evaluations,
    }
