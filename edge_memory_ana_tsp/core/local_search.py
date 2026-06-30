import itertools

from core.tsp_utils import is_valid_route
from core.tsp_utils import normalize_tour
from core.tsp_utils import route_edges
from core.tsp_utils import tour_cost


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
                    current_route = current_route.copy()
                    current_route[start_index:end_index + 1] = reversed(
                        current_route[start_index:end_index + 1]
                    )
                    current_route = normalize_tour(current_route)
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
                if not _are_edges_non_adjacent(
                    first_edge,
                    second_edge,
                    third_edge,
                    number_of_cities,
                ):
                    continue

                edge_triples_checked = edge_triples_checked + 1
                seen_reconnections = set()
                reconnections = _build_three_opt_reconnections(
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
                    if not _is_genuine_three_opt_candidate(
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
        current_route = two_opt_result["route"]
        current_fitness = two_opt_result["fitness"]
        two_opt_candidate_checks = (
            two_opt_candidate_checks + two_opt_result["candidate_checks"]
        )
        two_opt_improvements = two_opt_improvements + two_opt_result["improvements"]
        fitness_evaluations = (
            fitness_evaluations + two_opt_result["fitness_evaluations"]
        )

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
        current_route = three_opt_result["route"]


def _are_edges_non_adjacent(edge_a, edge_b, edge_c, number_of_cities):
    edge_indexes = [edge_a, edge_b, edge_c]
    for first_index in range(3):
        for second_index in range(first_index + 1, 3):
            difference = abs(edge_indexes[first_index] - edge_indexes[second_index])
            if difference == 1 or difference == number_of_cities - 1:
                return False
    return True


def _build_three_opt_reconnections(route, first_edge, second_edge, third_edge):
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
                    reversed_segment = segment.copy()
                    reversed_segment.reverse()
                    candidate = candidate + reversed_segment
                else:
                    candidate = candidate + segment
            reconnections.append(normalize_tour(candidate))

    return reconnections


def _is_genuine_three_opt_candidate(original_route, candidate_route):
    original_edges = route_edges(original_route)
    candidate_edges = route_edges(candidate_route)
    removed_edges = original_edges - candidate_edges
    added_edges = candidate_edges - original_edges
    return len(removed_edges) >= 3 and len(added_edges) >= 3
