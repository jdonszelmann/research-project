# from multiprocessing import Pool
import os
import pathlib
import re
from typing import Optional, Callable

import pysat
from mapf_branch_and_bound.bbsolver import compute_sol_cost
from tqdm import tqdm

from python.algorithm import MapfAlgorithm
from python.benchmarks.comparison import BCPInmatch, BCPPrematch, CBSPrematch, CBSInmatch, SATInmatch  # , EPEAStar, CBM, AStarODID,
from python.benchmarks.parse_map import MapParser
from python.benchmarks.run_with_timeout import run_with_timeout
# from python.benchmarks.comparison.icts import ICTS
from python.benchmarks.util import output_data

this_dir = pathlib.Path(__file__).parent.absolute()
name = "main"


def run(solver: Callable[[], MapfAlgorithm], bm_name: str, parse_maps: bool = True):
    batchdir = this_dir / name
    parser = MapParser(batchdir)

    fname = batchdir / f"results_{bm_name}.txt"
    fname2 = batchdir / f"actual_results_{bm_name}.txt"

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
        all_results = run_with_timeout(solver(), problems, parse_maps, 10)  # test with low timeout
        sols_inmatch, sols_costs = zip(*all_results)
        tqdm.write(f"{bm_name} with {num_agents} agents: {sols_inmatch}")
        times[num_agents] = sols_inmatch
        costs = []
        for sol in sols_costs:
            if sol:
                costs.append(compute_sol_cost(sol))
            else:
                costs.append(None)
        results[num_agents] = costs
        output_data(partname, times)
    # clean-up
    for file in os.listdir("temp"):
        os.remove("temp/" + file)

    tqdm.write(str(results))

    output_data(fname, times)
    output_data(fname2, results)

    return fname, bm_name


def main():
    batchdir = this_dir / name

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

    files.append(run(
        lambda: CBSPrematch(),
        "CBSPrematch"
    ))

    files.append(run(
        lambda: CBSInmatch(),
        "CBSInmatch"
    ))

    # files.append(run(
    #     lambda: SATInmatch(),
    #     "SATInmatch"
    # ))


if __name__ == '__main__':
    main()
