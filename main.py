from benchmarks import run_selected_benchmarks


EXPERIMENT_NAME = "baseline_parameters_v1"

ANA_EXPERIMENT = "v3"
# allowed: "baseline", "v1", "v2", "v3"


# True means run this benchmark.
# False means skip this benchmark.
BENCHMARK_MENU = {
    "square_4": False,
    "rectangle_6": False,
    "grid_9": False,
    "wi29": True,
    "dj38": False,
    "berlin52": False,
    "qa194": False,
}


BENCHMARK_PARAMETERS = {
    "square_4": {
        "number_of_runs": 10,
        "population_size": 10,
        "max_iterations": 100,
        "rho": 0.10,
        "temperature_start": 0.10,
        "temperature_min": 0.001,
    },

    "rectangle_6": {
        "number_of_runs": 10,
        "population_size": 10,
        "max_iterations": 200,
        "rho": 0.10,
        "temperature_start": 0.10,
        "temperature_min": 0.001,
    },

    "grid_9": {
        "number_of_runs": 30,
        "population_size": 20,
        "max_iterations": 700,
        "rho": 0.10,
        "temperature_start": 0.08,
        "temperature_min": 0.001,
    },

    "wi29": {
        "number_of_runs": 10,
        "population_size": 30,
        "max_iterations": 6666,
        "rho": 0.15,
        "temperature_start": 0.01,
        "temperature_min": 0.0001,
    },

    "dj38": {
        "number_of_runs": 10,
        "population_size": 50,
        "max_iterations": 2500,
        "rho": 0.10,
        "temperature_start": 0.07,
        "temperature_min": 0.0005,
    },

    "berlin52": {
        "number_of_runs": 10,
        "population_size": 60,
        "max_iterations": 3000,
        "rho": 0.08,
        "temperature_start": 0.06,
        "temperature_min": 0.0005,
    },

    "qa194": {
        "number_of_runs": 5,
        "population_size": 80,
        "max_iterations": 3000,
        "rho": 0.03,
        "temperature_start": 0.04,
        "temperature_min": 0.0005,
    },
}


if __name__ == "__main__":
    run_selected_benchmarks(
        BENCHMARK_MENU,
        BENCHMARK_PARAMETERS,
        EXPERIMENT_NAME,
        ANA_EXPERIMENT,
    )
