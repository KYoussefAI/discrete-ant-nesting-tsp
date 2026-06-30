import os


BENCHMARKS = {
    "square_4": {
        "known_optimum": 4.0,
        "use_integer_distances": False,
    },
    "rectangle_6": {
        "known_optimum": 10.0,
        "use_integer_distances": False,
    },
    "grid_9": {
        "known_optimum": 9.414213562373095,
        "use_integer_distances": False,
    },
    "wi29": {
        "known_optimum": 27603,
        "use_integer_distances": True,
        "file": os.path.join("data", "wi29.tsp"),
    },
    "dj38": {
        "known_optimum": 6656,
        "use_integer_distances": True,
        "file": os.path.join("data", "dj38.tsp"),
    },
}


DEFAULT_BENCHMARK_PARAMETERS = {
    "square_4": {
        "runs": 10,
        "population_size": 10,
        "max_iterations": 100,
        "rho": 0.10,
        "temperature_start": 0.10,
        "temperature_min": 0.001,
    },
    "rectangle_6": {
        "runs": 10,
        "population_size": 10,
        "max_iterations": 200,
        "rho": 0.10,
        "temperature_start": 0.10,
        "temperature_min": 0.001,
    },
    "grid_9": {
        "runs": 30,
        "population_size": 20,
        "max_iterations": 700,
        "rho": 0.10,
        "temperature_start": 0.08,
        "temperature_min": 0.001,
    },
    "wi29": {
        "runs": 10,
        "population_size": 30,
        "max_iterations": 6666,
        "rho": 0.20,
        "temperature_start": 0.03,
        "temperature_min": 0.0001,
    },
    "dj38": {
        "runs": 10,
        "population_size": 50,
        "max_iterations": 2500,
        "rho": 0.10,
        "temperature_start": 0.07,
        "temperature_min": 0.0005,
    },
}
