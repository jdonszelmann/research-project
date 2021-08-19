
from multiprocessing import Pool
from typing import Optional, Callable

from tqdm import tqdm

from python.algorithm import MapfAlgorithm
from python.benchmarks.RP.extensions_25percent_3teams import read_from_file
from python.benchmarks.graph_times import graph_results
from python.benchmarks.RP.inmatch_vs_prematch_75percent_1teams import output_data
import pathlib

from python.benchmarks.RP.parse_map import MapParser
from python.benchmarks.RP.run_with_timeout import run_with_timeout
from python.mstar.rewrite import Config, MatchingStrategy
from python.mstar.rewrite.config import GigaByte
from python.solvers.configurable_mstar_solver import ConfigurableMStar

this_dir = pathlib.Path(__file__).parent.absolute()
name = "comparison_obstacle_3teams_maps"
processes = 8

def run(solver: Callable[[], MapfAlgorithm], bm_name: str):
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
                sols_inmatch = run_with_timeout(p, solver(), problems, 2 * 60)

                tqdm.write(f"{bm_name} with {num_agents} agents: {sols_inmatch}")
                results[num_agents] = sols_inmatch
            else:
                results[num_agents] = [None for i in range(len(problems))]

            output_data(partname, results)

    tqdm.write(str(results))

    output_data(fname, results)

    return fname, bm_name


def main():
    batchdir = this_dir / name

    files: list[tuple[pathlib.Path, str]] = []

    files.append(run(
        lambda: ConfigurableMStar(
            Config(
                operator_decomposition=True,
                precompute_paths=False,
                precompute_heuristic=True,
                collision_avoidance_table=False,
                recursive=False,
                matching_strategy=MatchingStrategy.SortedPruningPrematch,
                max_memory_usage=3 * GigaByte,
                debug=False,
                report_expansions=False,
            ),
        ),
        "M*"
    ))

    graph_results(
        *files,
        batchdir / f"{name}",
        save=True,
        bounds=False,
    )


if __name__ == '__main__':
    main()


