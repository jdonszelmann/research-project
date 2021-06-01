from multiprocessing import Pool
from typing import Optional

from tqdm import tqdm

from python.benchmarks.inmatch_vs_prematch_75percent_1teams import generate_maps
import pathlib

from python.benchmarks.parse_map import MapParser
from python.benchmarks.run_with_timeout import run_with_timeout
from python.mstar.rewrite import Config, MatchingStrategy
from python.mstar.rewrite.config import GigaByte
from python.solvers.configurable_mstar_solver import ConfigurableMStar

import copy

this_dir = pathlib.Path(__file__).parent.absolute()
name = "inmatch_vs_prematch_75percent_1teams_maps"
processes = 10

inmatch_config = Config(
    operator_decomposition=False,
    precompute_paths=False,
    precompute_heuristic=True,
    collision_avoidance_table=False,
    recursive=False,
    matching_strategy=MatchingStrategy.Inmatch,
    max_memory_usage=3 * GigaByte,
    debug=False,
    report_expansions=True,
)


prematch_config = Config(
    operator_decomposition=False,
    precompute_paths=False,
    precompute_heuristic=True,
    collision_avoidance_table=False,
    recursive=False,
    matching_strategy=MatchingStrategy.Prematch,
    max_memory_usage=3 * GigaByte,
    debug=False,
    report_expansions=True,
)


def run_benchmark():
    batchdir = this_dir / name
    parser = MapParser(batchdir)

    # num agents : solutions
    inmatch: dict[int, list[Optional[float]]] = {}
    prematch: dict[int, list[Optional[float]]] = {}

    inmatch_exp: dict[int, list[int]] = {}
    prematch_exp: dict[int, list[int]] = {}

    all_problems = [[i[1] for i in parser.parse_batch(name.name)] for name in batchdir.iterdir() if name.is_dir()]
    all_problems.sort(key=lambda i: len(i[0].goals))

    with Pool(processes) as p:
        for problems in tqdm(all_problems):
            num_agents = len(problems[0].goals)

            if num_agents <= 1 or sum(1 for i in inmatch[num_agents - 1] if i is not None) != 0:
                path = run_with_timeout(p, ConfigurableMStar(
                    inmatch_config
                ), problems, 2 * 60)

                print("\n")
                print(len(inmatch_config.expansions), sum(inmatch_config.expansions))
                print("\n")

                inmatch_exp[num_agents] = copy.deepcopy(inmatch_config.expansions)
                inmatch_config.expansions = []

                inmatch[num_agents] = path
            else:
                inmatch[num_agents] = [None for i in range(len(problems))]

            if num_agents <= 1 or sum(1 for i in prematch[num_agents - 1] if i is not None) != 0:
                path = run_with_timeout(p, ConfigurableMStar(
                    prematch_config
                ), problems, 2 * 60)

                print("\n")
                print(len(prematch_config.expansions), sum(prematch_config.expansions))
                print("\n")

                prematch_exp[num_agents] = copy.deepcopy(prematch_config.expansions)
                prematch_config.expansions = []


                prematch[num_agents] = path
            else:
                prematch[num_agents] = [None for i in range(len(problems))]


    tqdm.write(str(inmatch_exp))
    tqdm.write(str(prematch_exp))

    output_data(batchdir / "results_inmatch_expansion.txt", inmatch)
    output_data(batchdir / "results_prematch_expansion.txt", inmatch)


def output_data(file: pathlib.Path, data: dict[int, list[float]]):
    with open(file, "w") as f:
        for i, r in sorted([(a, b) for a, b in data.items()], key=lambda x: x[0]):
            f.write(f"{i}: {r}")



if __name__ == '__main__':
    batchdir = this_dir / name

    generate_maps()
    run_benchmark()

    # graph_results(
    #     # ("results_inmatch.txt", "inmatch"),
    #     (batchdir / "results_prematch.txt", "pruning prematch")
    # )
