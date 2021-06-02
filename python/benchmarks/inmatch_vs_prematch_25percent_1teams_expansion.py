from multiprocessing import Pool
from typing import Optional

from tqdm import tqdm

from python.benchmarks.graph_output import graph_results
from python.benchmarks.inmatch_vs_prematch_25percent_1teams import generate_maps
import pathlib

from python.benchmarks.parse_map import MapParser
from python.benchmarks.run_with_timeout_expansion import run_with_expansion_timeout
from python.mstar.rewrite import Config, MatchingStrategy
from python.mstar.rewrite.config import GigaByte
from python.solvers.configurable_mstar_solver import ConfigurableMStar

import copy

this_dir = pathlib.Path(__file__).parent.absolute()
name = "inmatch_vs_prematch_25percent_1teams_maps"
processes = 3

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
    inmatch: dict[int, list[Optional[list[int]]]] = {}
    prematch: dict[int, list[Optional[list[int]]]] = {}

    all_problems = [[i[1] for i in parser.parse_batch(name.name)] for name in batchdir.iterdir() if name.is_dir()]
    all_problems.sort(key=lambda i: len(i[0].goals))
    with open(batchdir / "results_inmatch_expansion.txt", "w") as imf:
        with open(batchdir / "results_prematch_expansion.txt", "w") as pmf:

            with Pool(processes) as p:
                for problems in tqdm(all_problems):
                    num_agents = len(problems[0].goals)

                    if num_agents <= 1 or sum(1 for i in inmatch[num_agents - 1] if i is not None) != 0:
                        expansions = run_with_expansion_timeout(p, ConfigurableMStar(
                            inmatch_config
                        ), problems, 2 * 60)

                        print([i for i in range(1000)])
                        print("\n\n\n")
                        print(f"{sum(len(i) for i in expansions if i is not None), sum(sum(i) for i in expansions if i is not None)}")
                        print("\n\n\n")

                        inmatch[num_agents] = expansions
                        imf.writelines([f"{num_agents}: {expansions}"])
                    else:
                        inmatch[num_agents] = [None for i in range(len(problems))]

                    if num_agents <= 1 or sum(1 for i in prematch[num_agents - 1] if i is not None) != 0:
                        expansions = run_with_expansion_timeout(p, ConfigurableMStar(
                            prematch_config
                        ), problems, 2 * 60)

                        print([i for i in range(1000)])
                        print("\n\n\n")
                        print(f"{sum(len(i) for i in expansions if i is not None), sum(sum(i) for i in expansions if i is not None)}")
                        print("\n\n\n")

                        pmf.writelines([f"{num_agents}: {expansions}"])
                        prematch[num_agents] = expansions
                    else:
                        prematch[num_agents] = [None for i in range(len(problems))]





if __name__ == '__main__':
    batchdir = this_dir / name

    generate_maps()
    run_benchmark()

    # graph_results(
    #     # ("results_inmatch_tmp.txt", "inmatch"),
    #     (batchdir / "results_prematch.txt", "pruning prematch")
    # )
