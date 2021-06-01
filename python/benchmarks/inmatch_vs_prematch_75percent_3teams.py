from multiprocessing import Pool
from typing import Optional

from mapfmclient import Problem
from tqdm import tqdm

from python.benchmarks.map import MapGenerator
import pathlib

from python.benchmarks.parse_map import MapParser
from python.benchmarks.run_with_timeout import run_with_timeout
from python.mstar.rewrite import Config, MatchingStrategy
from python.mstar.rewrite.config import GigaByte
from python.solvers.configurable_mstar_solver import ConfigurableMStar

this_dir = pathlib.Path(__file__).parent.absolute()
name = "inmatch_vs_prematch_75percent_3teams_maps"
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
            max_neighbors=1
        )




def run_benchmark():
    batchdir = this_dir / name
    parser = MapParser(batchdir)

    # num agents : solutions
    inmatch: dict[int, list[Optional[float]]] = {}
    prematch: dict[int, list[Optional[float]]] = {}

    all_problems = [[i[1] for i in parser.parse_batch(name.name)] for name in batchdir.iterdir()]
    all_problems.sort(key=lambda i: len(i[0].goals))

    with Pool(processes) as p:
        for problems in tqdm(all_problems):
            num_agents = len(problems[0].goals)

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

            if num_agents > 1 and sum(1 for i in prematch[num_agents - 1] if i is not None) != 0:
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



if __name__ == '__main__':
    generate_maps()
    run_benchmark()
