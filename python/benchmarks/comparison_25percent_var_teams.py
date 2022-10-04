import os
import pathlib
import re
from typing import Optional, Callable

from tqdm import tqdm

from python.algorithm import MapfAlgorithm
from python.benchmarks.comparison import BCPInmatch, BCPPrematch, CBSInmatch, CBSPrematch  # , EPEAStar, CBM, AStarODID,
from python.benchmarks.graph_times import graph_results
from python.benchmarks.map import MapGenerator
from python.benchmarks.parse_map import MapParser
from python.benchmarks.run_with_timeout import run_with_timeout
# from python.benchmarks.comparison.icts import ICTS
from python.benchmarks.util import read_from_file, output_data

this_dir = pathlib.Path(__file__).parent.absolute()
name = "comparison_25percent_var_teams_maps_preview_2"
processes = 1


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def generate_maps():
    path = this_dir / name
    print(path)
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        pass

    num = 24

    dirnames = [n.name for n in path.iterdir() if n.is_dir()]

    for i in tqdm([1, 2, 3, 4, 6, 12, 24]):
        if any(f"T{i}" in dirname for dirname in dirnames):
            tqdm.write(f"maps for {i} agents already generated")
            continue
        else:
            tqdm.write(f"generating {path}")

        map_generator = MapGenerator(path)
        map_generator.generate_even_batch(
            10,  # number of maps
            20, 20,  # size
            num,  # number of agents
            i,  # number of teams
            prefix=name,
            min_goal_distance=0,
            open_factor=0.65,
            max_neighbors=3,
        )


def run(solver: Callable[[], MapfAlgorithm], bm_name: str, parse_maps: bool = True):
    batchdir = this_dir / name
    parser = MapParser(batchdir)

    fname = batchdir / f"results_{bm_name}.txt"

    if fname.exists():
        print(f"data exists for {bm_name}")
        return fname, bm_name

    # num agents : solutions
    results: dict[int, list[Optional[float]]] = {}

    all_problems = [parser.parse_batch(n.name) for n in batchdir.iterdir() if n.is_dir()]
    all_problems.sort(key=lambda i: natural_keys(i[0][0]))
    for problem_list in all_problems:
        for problem in problem_list:
            problem[1].name = problem[0]

    # with Pool(processes = 1) as p:
    for problems in tqdm(all_problems):
        teams = problems[0][1].goals[-1].color + 1
        partname = pathlib.Path(str(fname) + f".{teams}teams")
        if partname.exists():
            print(f"found data for part {teams}")
            results[teams] = read_from_file(partname, teams)
            continue
        prev_team = [1, 2, 3, 4, 6, 12][[1, 2, 3, 4, 6, 12].index(teams) - 1]
        if teams == 1 or sum(1 for i in results[prev_team] if i is not None) != 0:
            # sols_inmatch = run_with_timeout(p, solver(), problems, parse_maps, 1 * 1) # test with low timeout
            sols_inmatch = run_with_timeout(solver(), problems, parse_maps, 60)  # test with low timeout

            tqdm.write(f"{bm_name} with {teams} teams: {sols_inmatch}")
            results[teams] = sols_inmatch
        else:
            results[teams] = [None for i in range(len(problems))]

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

    files.append(run(
        lambda: BCPInmatch(),
        "BCPInmatch"
    ))

    # files.append(run(
    #     lambda: CBSPrematch(),
    #     "CBSPrematch"
    # ))

    files.append(run(
        lambda: CBSInmatch(),
        "CBSInmatch"
    ))

    graph_results(
        *files,
        batchdir / f"{name}",
        save=True,
        bounds=False,
        legend=False,
    )


if __name__ == '__main__':
    main()
