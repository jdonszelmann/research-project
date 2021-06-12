from multiprocessing import Pool
from typing import Optional

from mapfmclient import Problem
from tqdm import tqdm

from python.benchmarks.extensions_25percent_3teams import read_from_file
from python.benchmarks.graph_times import graph_results
from python.benchmarks.inmatch_vs_prematch_75percent_1teams import output_data
from python.benchmarks.map import MapGenerator
import pathlib

from python.benchmarks.parse_map import MapParser
from python.benchmarks.run_with_timeout import run_with_timeout
from python.mstar.rewrite import Config, MatchingStrategy
from python.mstar.rewrite.config import GigaByte
from python.solvers.configurable_mstar_solver import ConfigurableMStar

this_dir = pathlib.Path(__file__).parent.absolute()
name = "extensions_75percent_1teams_maps"
processes = 1


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
            1,  # number of teams
            prefix=name,
            min_goal_distance=0,
            open_factor=0.65,
            max_neighbors=1
        )


def run(config: Config, bm_name: str):
    batchdir = this_dir / name
    parser = MapParser(batchdir)

    fname = batchdir / f"results_{bm_name}.txt"

    if fname.exists():
        print(f"data exists for {bm_name}")
        return fname, bm_name

    # num agents : solutions
    results: dict[int, list[Optional[float]]] = {}

    all_problems = [[i[1] for i in parser.parse_batch(n.name)] for n in batchdir.iterdir() if n.is_dir()]
    all_problems.sort(key=lambda i: len(i[0].goals))

    with Pool(processes) as p:
        for problems in tqdm(all_problems):
            num_agents = len(problems[0].goals)

            partname = pathlib.Path(str(fname) + f".{num_agents}agents")
            if partname.exists():
                print(f"found data for part {num_agents}")
                results[num_agents] = read_from_file(partname, num_agents)
                continue

            if num_agents <= 1 or sum(1 for i in results[num_agents - 1] if i is not None) != 0:
                sols_inmatch = run_with_timeout(p, ConfigurableMStar(
                    config
                ), problems, 2 * 60)

                tqdm.write(f"{bm_name} with {num_agents} agents: {sols_inmatch}")
                results[num_agents] = sols_inmatch
            else:
                results[num_agents] = [None for i in range(len(problems))]

            output_data(partname, results)

    tqdm.write(str(results))

    output_data(fname, results)

    return fname, bm_name



if __name__ == '__main__':
    batchdir = this_dir / name

    generate_maps()
    files: list[tuple[pathlib.Path, str]] = []

    files.append(run(
        Config(
            operator_decomposition=False,
            precompute_paths=False,
            precompute_heuristic=False,
            collision_avoidance_table=False,
            recursive=False,
            matching_strategy=MatchingStrategy.Prematch,
            max_memory_usage=3 * GigaByte,
            debug=False,
            report_expansions=True,
        ),
        "no extensions"
    ))

    files.append(run(
        Config(
            operator_decomposition=False,
            precompute_paths=False,
            precompute_heuristic=False,
            collision_avoidance_table=False,
            recursive=False,
            matching_strategy=MatchingStrategy.PruningPrematch,
            max_memory_usage=3 * GigaByte,
            debug=False,
            report_expansions=True,
        ),
        "pruning"
    ))

    files.append(run(
        Config(
            operator_decomposition=False,
            precompute_paths=False,
            precompute_heuristic=False,
            collision_avoidance_table=False,
            recursive=False,
            matching_strategy=MatchingStrategy.SortedPruningPrematch,
            max_memory_usage=3 * GigaByte,
            debug=False,
            report_expansions=True,
        ),
        "pruning and sorting"
    ))

    files.append(run(
        Config(
            operator_decomposition=False,
            precompute_paths=False,
            precompute_heuristic=True,
            collision_avoidance_table=False,
            recursive=False,
            matching_strategy=MatchingStrategy.SortedPruningPrematch,
            max_memory_usage=3 * GigaByte,
            debug=False,
            report_expansions=True,
        ),
        "precomputed heuristic"
    ))

    files.append(run(
        Config(
            operator_decomposition=True,
            precompute_paths=False,
            precompute_heuristic=True,
            collision_avoidance_table=False,
            recursive=False,
            matching_strategy=MatchingStrategy.SortedPruningPrematch,
            max_memory_usage=3 * GigaByte,
            debug=False,
            report_expansions=True,
        ),
        "operator decomposition"
    ))

    graph_results(
        *files,
        batchdir / f"{name}",
        save=True,
        bounds=False,
    )
