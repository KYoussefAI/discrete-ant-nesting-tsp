from benchmarks import run_selected_benchmarks


EXPERIMENT_NAME = "edge-memory-ana-final"

ANA_EXPERIMENT = "v11"
# allowed: "baseline", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12"


# True means run this benchmark.
# False means skip this benchmark.
BENCHMARK_MENU = {
    "square_4": True,
    "rectangle_6": True,
    "grid_9": True,
    "wi29": True,
    "dj38": True,
}

# BENCHMARK_MENU = {
#     "square_4": True,
#     "rectangle_6": True,
#     "grid_9": True,
#     "wi29": True,
#     "dj38": True,
# }


BENCHMARK_PARAMETERS = {
    "square_4": {
        "number_of_runs": 10,
        "population_size": 10,
        "max_iterations": 100,
        "rho": 0.10,
        "temperature_start": 0.10,
        "temperature_min": 0.001,
        "two_opt_trigger_temperature_start": 0.10,
        "two_opt_trigger_temperature_min": 0.001,
    },

    "rectangle_6": {
        "number_of_runs": 10,
        "population_size": 10,
        "max_iterations": 200,
        "rho": 0.10,
        "temperature_start": 0.10,
        "temperature_min": 0.001,
        "two_opt_trigger_temperature_start": 0.10,
        "two_opt_trigger_temperature_min": 0.001,
    },

    "grid_9": {
        "number_of_runs": 30,
        "population_size": 20,
        "max_iterations": 700,
        "rho": 0.10,
        "temperature_start": 0.08,
        "temperature_min": 0.001,
        "two_opt_trigger_temperature_start": 0.08,
        "two_opt_trigger_temperature_min": 0.001,
    },

    "wi29": {
        "number_of_runs": 10,
        "population_size": 30,
        "max_iterations": 6666,
        "rho": 0.20,
        "temperature_start": 0.03,
        "temperature_min": 0.0001,
        "edge_memory_initial": 1.0,
        "edge_memory_evaporation_rate": 0.02,
        "edge_memory_max": 10.0,
        "global_best_deposit": 1.0,
        "near_best_deposit": 0.3,
        "near_best_gap": 0.03,
        "memory_max_edge_moves": 3,
        "memory_top_k_edges": 20,
        "memory_candidate_pool_size": 100,
        "use_distance_weighted_memory": True,
    },

    "dj38": {
        "number_of_runs": 10,
        "population_size": 50,
        "max_iterations": 2500,
        "rho": 0.10,
        "temperature_start": 0.07,
        "temperature_min": 0.0005,
        "two_opt_trigger_temperature_start": 0.07,
        "two_opt_trigger_temperature_min": 0.0005,
    },

}


if __name__ == "__main__":
    run_selected_benchmarks(
        BENCHMARK_MENU,
        BENCHMARK_PARAMETERS,
        EXPERIMENT_NAME,
        ANA_EXPERIMENT,
    )
