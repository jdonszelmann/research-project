# from multiprocessing import Pool
import os
import pathlib
from typing import Optional, Callable

import yaml
from tqdm import tqdm

from graph_times import graph_results
from map import MapGenerator
from python.algorithm import MapfAlgorithm
from python.benchmarks.comparison import CBSTA
from python.benchmarks.parse_map import MapParser
from python.benchmarks.run_with_timeout import run_with_timeout
# from python.benchmarks.comparison.icts import ICTS
from python.benchmarks.util import output_data, read_from_file

this_dir = pathlib.Path(__file__).parent.absolute()
name = "main"


def generate_maps():
    path = this_dir / name
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        pass

    num = 2

    dirnames = [n.name for n in path.iterdir() if n.is_dir()]

    for i in tqdm(range(1, num + 1)):
        if any(f"A{i}" in dirname for dirname in dirnames):
            tqdm.write(f"maps for {i} agents already generated")
            continue
        else:
            tqdm.write(f"generating {path}")

        map_generator = MapGenerator(path)
        map_generator.generate_even_batch(
            1,  # number of maps
            10, 10,  # size
            i,  # number of agents
            1,  # number of teams
            prefix=name,
            min_goal_distance=0,
            open_factor=0.65,
            max_neighbors=3,
        )


def run(solver: Callable[[], MapfAlgorithm], bm_name: str, parse_maps: bool = True):
    batchdir = this_dir / name
    parser = MapParser(batchdir)

    fname = batchdir / f"results_{bm_name}.txt"

    # if fname.exists():
    #     print(f"data exists for {bm_name}")
    #     return fname, bm_name

    # num agents : solutions
    results: dict[int, list[Optional[int]]] = {}
    times: dict[int, list[Optional[float]]] = {}

    all_problems = [parser.parse_batch(n.name) for n in batchdir.iterdir() if n.is_dir()]
    all_problems.sort(key=lambda i: len(i[0][1].goals))
    for problem_list in all_problems:
        for problem in problem_list:
            problem[1].name = problem[0]

    # with Pool(processes = 1) as p:
    for problems in all_problems:
        num_agents = len(problems[0][1].goals)

        partname = pathlib.Path(str(fname) + f".{num_agents}agents")
        # if partname.exists():
        #     print(f"found data for part {num_agents}")
        #     results[num_agents] = read_from_file(partname, num_agents)
        #     continue
        all_results = run_with_timeout(solver(), problems, parse_maps, 1000000)  # test with low timeout
        sols_inmatch, _ = zip(*all_results)
        tqdm.write(f"{bm_name} with {num_agents} agents: {sols_inmatch}")
        times[num_agents] = sols_inmatch
        output_data(partname, times)
    # clean-up
    # for file in os.listdir("temp"):
    #     os.remove("temp/" + file)

    tqdm.write(str(results))

    output_data(fname, times)

    return fname, bm_name


def main():
    batchdir = this_dir / name

    files: list[tuple[pathlib.Path, str]] = []

    # files.append(run(
    #     lambda: BCPPrematch(),
    #     "BCPPrematch"
    # ))
    #
    # files.append(run(
    #     lambda: BCPInmatch(),
    #     "BCPInmatch"
    # ))
    #
    # files.append(run(
    #     lambda: CBSPrematch(),
    #     "CBSPrematch"
    # ))
    #
    # files.append(run(
    #     lambda: CBSInmatch(),
    #     "CBSInmatch"
    # ))

    files.append(run(
        lambda: CBSTA(),
        "CBS-TA"
    ))

    # files.append(run(
    #     lambda: SATInmatch(),
    #     "SATInmatch"
    # ))
    #
    # files.append(run(
    #     lambda: SATPrematch(),
    #     "SATPrematch"
    # ))

    # graph_results(
    #     *files,
    #     batchdir / f"{name}",
    #     under="number of agents",
    #     save=False,
    #     bounds=False,
    #     legend=False,
    #     limit=100,
    # )


if __name__ == '__main__':
    main()
