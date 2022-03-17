# from multiprocessing import Pool
from typing import Optional, Callable

from tqdm import tqdm

from python.algorithm import MapfAlgorithm
from python.benchmarks.comparison import BCPPrematch, BCPInmatch #, EPEAStar, CBM, AStarODID,
#from python.benchmarks.comparison.icts import ICTS
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

import os

this_dir = pathlib.Path(__file__).parent.absolute()
name = "comparison_75percent_3teams_maps"
# processes = 1


def generate_maps():
    path = this_dir / name
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        pass

    num = 25

    dirnames = [n.name for n in path.iterdir() if n.is_dir()]

    for i in tqdm(range(1, num + 1)):
        if any(f"A{i}" in dirname for dirname in dirnames):
            tqdm.write(f"maps for {i} agents already generated")
            continue
        else:
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
            max_neighbors=1,
        )


def run(solver: Callable[[], MapfAlgorithm], bm_name: str, parse_maps : bool = True):
    batchdir = this_dir / name
    parser = MapParser(batchdir)
    
    fname = batchdir / f"results_{bm_name}.txt"

    if fname.exists():
        print(f"data exists for {bm_name}")
        return fname, bm_name

    # num agents : solutions
    results: dict[int, list[Optional[float]]] = {}

    all_problems = [parser.parse_batch(n.name) for n in batchdir.iterdir() if n.is_dir()]
    all_problems.sort(key=lambda i: len(i[0][1].goals))
    for problem_list in all_problems:
        for problem in problem_list:
            problem[1].name = problem[0]

    #with Pool(processes = 1) as p:
    for problems in tqdm(all_problems):
        num_agents = len(problems[0][1].goals)
        
        partname = pathlib.Path(str(fname) + f".{num_agents}agents")
        if partname.exists():
            print(f"found data for part {num_agents}")
            results[num_agents] = read_from_file(partname, num_agents)
            continue
        if num_agents <= 2 or sum(1 for i in results[num_agents - 1] if i is not None) != 0:
            #sols_inmatch = run_with_timeout(p, solver(), problems, parse_maps, 1 * 1) # test with low timeout
            sols_inmatch = run_with_timeout(solver(), problems, parse_maps, 1 * 1) # test with low timeout

            tqdm.write(f"{bm_name} with {num_agents} agents: {sols_inmatch}")
            results[num_agents] = sols_inmatch
        else:
            results[num_agents] = [None for i in range(len(problems))]

        output_data(partname, results)
    # clean-up
    for file in os.listdir("temp"):
        os.remove("temp/" + file)

    tqdm.write(str(results))

    output_data(fname, results)

    return fname, bm_name



def main():
    batchdir = this_dir / name

    generate_maps()
    files: list[tuple[pathlib.Path, str]] = []

    # files.append(run(
    #     lambda: ConfigurableMStar(
    #         Config(
    #             operator_decomposition=True,
    #             precompute_paths=False,
    #             precompute_heuristic=True,
    #             collision_avoidance_table=False,
    #             recursive=False,
    #             matching_strategy=MatchingStrategy.SortedPruningPrematch,
    #             max_memory_usage=3 * GigaByte,
    #             debug=False,
    #             report_expansions=False,
    #         ), 
    #     ),
    #     "M*"
    # ))

    # files.append(run(
    #     lambda: EPEAStar(),
    #     "EPEA*"
    # ))

    # files.append(run(
    #     lambda: CBM(),
    #     "CBM"
    # ))

    # files.append(run(
    #     lambda: AStarODID(),
    #     "A*-OD-ID"
    # ))

    # files.append(run(
    #     lambda: ICTS(),
    #     "ICTS"
    # ))

    files.append(run(
        lambda: BCPPrematch(),
        "BCPPrematch"
    ))

    # files.append(run(
    #     lambda: BCPInmatch(),
    #     "BCPInmatch"
    # ))

    graph_results(
        *files,
        batchdir / f"{name}",
        save=True,
        bounds=False,
        legend=False,
    )


if __name__ == '__main__':
    main()
