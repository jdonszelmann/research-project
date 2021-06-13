from multiprocessing import Pool
from typing import Optional

from mapfmclient import Problem
from tqdm import tqdm

from python.benchmarks.graph_times import graph_results
from python.benchmarks.map import MapGenerator
import pathlib

from python.benchmarks.parse_map import MapParser
from python.benchmarks.run_with_timeout import run_with_timeout
from python.mstar.rewrite import Config, MatchingStrategy
from python.mstar.rewrite.config import GigaByte
from python.solvers.configurable_mstar_solver import ConfigurableMStar

this_dir = pathlib.Path(__file__).parent.absolute()
name = "inmatch_vs_prematch_25percent_3teams_maps"
processes = 10

def generate_maps():
    path = this_dir / name
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        print("maps already generated")
        return

    for i in tqdm(range(1, 16)):
        tqdm.write(f"generating {path}")

        map_generator = MapGenerator(path)
        map_generator.generate_even_batch(
            200,  # number of maps
            20, 20,  # size
            i,  # number of agents
            3,  # number of teams
            prefix=name,
            min_goal_distance=0,
            open_factor=0.65,
            max_neighbors=3
        )


def run_benchmark():
    batchdir = this_dir / name
    parser = MapParser(batchdir)

    if (batchdir / "results_inmatch.txt").exists():
        print("data exists")
        return

    if (batchdir / "results_prematch.txt").exists():
        print("data exists")
        return

    # num agents : solutions
    inmatch: dict[int, list[Optional[float]]] = {}
    prematch: dict[int, list[Optional[float]]] = {}

    all_problems = [[i[1] for i in parser.parse_batch(name.name)] for name in batchdir.iterdir() if name.is_dir()]
    all_problems.sort(key=lambda i: len(i[0].goals))

    with Pool(processes) as p:
        for problems in tqdm(all_problems):
            num_agents = len(problems[0].goals)

            print("inmatch")
            if num_agents <= 1 or sum(1 for i in inmatch[num_agents - 1] if i is not None) != 0:
                sols_inmatch = run_with_timeout(p, ConfigurableMStar(
                    Config(
                        operator_decomposition=False,
                        precompute_paths=False,
                        precompute_heuristic=True,
                        collision_avoidance_table=False,
                        recursive=False,
                        matching_strategy=MatchingStrategy.Inmatch,
                        max_memory_usage=3 * GigaByte,
                        debug=False,
                    )
                ), problems, 2 * 60)

                tqdm.write(f"inmatch with {num_agents} agents: {sols_inmatch}")
                inmatch[num_agents] = sols_inmatch
            else:
                inmatch[num_agents] = [None for i in range(len(problems))]

            print("prematch")
            if num_agents <= 1 or sum(1 for i in prematch[num_agents - 1] if i is not None) != 0:
                sols_prematch = run_with_timeout(p, ConfigurableMStar(
                    Config(
                        operator_decomposition=False,
                        precompute_paths=False,
                        precompute_heuristic=True,
                        collision_avoidance_table=False,
                        recursive=False,
                        matching_strategy=MatchingStrategy.Prematch,
                        max_memory_usage=3 * GigaByte,
                        debug=False,
                    )
                ), problems, 2 * 60)

                tqdm.write(f"prematch with {num_agents} agents: {sols_prematch}")
                prematch[num_agents] = sols_prematch
            else:
                prematch[num_agents] = [None for i in range(len(problems))]

    tqdm.write(str(inmatch))
    tqdm.write(str(prematch))

    output_data(batchdir / "results_inmatch.txt", inmatch)
    output_data(batchdir / "results_prematch.txt", prematch)


def output_data(file: pathlib.Path, data: dict[int, list[float]]):
    with open(file, "w") as f:
        for i, r in sorted([(a, b) for a, b in data.items()], key=lambda x: x[0]):
            f.write(f"{i}: {r}\n")


def main():
    batchdir = this_dir / name

    generate_maps()
    run_benchmark()

    graph_results(
        (batchdir / "results_inmatch.txt", "inmatch"),
        (batchdir / "results_prematch.txt", "prematch"),
        batchdir / f"{name}"
    )


if __name__ == '__main__':
    main()
