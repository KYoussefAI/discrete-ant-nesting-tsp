import math


def normal_round(value):
    return math.floor(value + 0.5)


def euclidean_distance(point_a, point_b):
    x_difference = point_a[0] - point_b[0]
    y_difference = point_a[1] - point_b[1]
    return math.sqrt(x_difference ** 2 + y_difference ** 2)


def build_distance_matrix(coordinates, use_integer_distances=False):
    distance_matrix = []
    for point_a in coordinates:
        row = []
        for point_b in coordinates:
            distance_value = euclidean_distance(point_a, point_b)
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
        city_b = route[(index + 1) % number_of_cities]
        total = total + distance_matrix[city_a][city_b]
    return total


def normalize_tour(route):
    number_of_cities = len(route)
    zero_index = route.index(0)
    forward = []
    for offset in range(number_of_cities):
        forward.append(route[(zero_index + offset) % number_of_cities])

    reverse = [0]
    for index in range(number_of_cities - 1, 0, -1):
        reverse.append(forward[index])

    if reverse < forward:
        return reverse
    return forward


def is_valid_route(route, number_of_cities):
    return sorted(route) == list(range(number_of_cities))


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


def create_initial_route(number_of_cities, rng):
    other_cities = list(range(1, number_of_cities))
    rng.shuffle(other_cities)
    return normalize_tour([0] + other_cities)


def build_swap_sequence(current, target):
    working = current.copy()
    swaps = []
    positions = {}
    for index in range(len(working)):
        positions[working[index]] = index

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


def introduce_edge_with_reversal(route, edge):
    city_a = edge[0]
    city_b = edge[1]
    position_a = route.index(city_a)
    position_b = route.index(city_b)
    if position_a > position_b:
        position_a, position_b = position_b, position_a

    new_route = route.copy()
    new_route[position_a + 1:position_b + 1] = reversed(
        new_route[position_a + 1:position_b + 1]
    )
    return normalize_tour(new_route)


def random_segment_inversion(route, movement_strength, rng):
    new_route = route.copy()
    maximum_length = len(route) - 2
    if maximum_length < 2:
        maximum_length = 2
    segment_length = movement_strength + 1
    if segment_length < 2:
        segment_length = 2
    if segment_length > maximum_length:
        segment_length = maximum_length

    first_index = rng.randint(1, len(route) - segment_length)
    last_index = first_index + segment_length
    new_route[first_index:last_index] = reversed(new_route[first_index:last_index])
    return normalize_tour(new_route)


def load_tsplib_coordinates(file_path):
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
                    coordinates.append((int(parts[0]), float(parts[1]), float(parts[2])))
                continue

            if line.startswith("TYPE"):
                if _header_value(line) != "TSP":
                    raise ValueError("Unsupported TSPLIB TYPE in " + file_path)
            elif line.startswith("DIMENSION"):
                dimension = int(_header_value(line))
            elif line.startswith("EDGE_WEIGHT_TYPE"):
                edge_weight_type = _header_value(line)
            elif line == "NODE_COORD_SECTION":
                reading_coordinates = True

    if edge_weight_type != "EUC_2D":
        raise ValueError("Unsupported EDGE_WEIGHT_TYPE in " + file_path)
    if dimension is None:
        raise ValueError("Missing DIMENSION in " + file_path)
    if len(coordinates) != dimension:
        raise ValueError("Coordinate count does not match DIMENSION in " + file_path)

    coordinates.sort()
    return [(item[1], item[2]) for item in coordinates]


def _header_value(line):
    if ":" not in line:
        return ""
    return line.split(":", 1)[1].strip()
