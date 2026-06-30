import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.algorithm_flow import run_edge_memory_ana_tsp
from core.tsp_utils import is_valid_route
from tsp_problems import PROBLEMS


def main():
    result = run_edge_memory_ana_tsp(
        PROBLEMS["square_4"],
        population_size=5,
        max_iterations=20,
        seed=1,
        rho=0.10,
        temperature_start=0.10,
        temperature_min=0.001,
    )
    if result["best_fitness"] != 4.0:
        raise AssertionError("Expected square_4 optimum 4.0")
    if not is_valid_route(result["best_route"], len(PROBLEMS["square_4"])):
        raise AssertionError("Smoke test produced an invalid route")

    print("smoke_test passed")
    print("best_fitness =", result["best_fitness"])
    print("best_route =", result["best_route"])


if __name__ == "__main__":
    main()
