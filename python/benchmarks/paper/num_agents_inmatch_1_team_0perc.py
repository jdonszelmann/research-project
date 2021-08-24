from multiprocessing import Pool
from typing import Optional, Callable

from tqdm import tqdm

from python.algorithm import MapfAlgorithm
from python.benchmarks.comparison import EPEAStar, CBM, AStarODIDInmatch, ICTSInmatching
from python.benchmarks.RP.extensions_25percent_3teams import read_from_file
from python.benchmarks.graph_times import graph_results
from python.benchmarks.RP.inmatch_vs_prematch_75percent_1teams import output_data
import pathlib

from python.benchmarks.RP.parse_map import MapParser
from python.benchmarks.RP.run_with_timeout import run_with_timeout
from python.benchmarks.map2 import MapGenerator2
from python.mstar.rewrite import Config, MatchingStrategy
from python.mstar.rewrite.config import GigaByte
from python.solvers.configurable_mstar_solver import ConfigurableMStar

this_dir = pathlib.Path(__file__).parent.absolute()
name = "num_agents_inmatch_1_team"
processes = 10

timeout = 2 * 60

def generate_maps():
    path = this_dir / name
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        pass

    dirnames = [n.name for n in path.iterdir() if n.is_dir()]

    for i in tqdm(range(3, 24)):

        map_generator = MapGenerator2(path)
        map_generator.generate_even_batch(
            100,  # number of maps
            20, 20,  # size
            i,
            1,  # number of teams
            prefix=name,
            obstacle_percentage=0
        )


def run(solver: Callable[[], MapfAlgorithm], bm_name: str):
    batchdir = this_dir / name
    parser = MapParser(batchdir)

    fname = batchdir / f"results_{bm_name}.txt"

    if fname.exists():
        print(f"data exists for {bm_name}")
        return fname, bm_name

    # num agents : solutions
    results: dict[int, list[Optional[float]]] = {}

    all_problems = [(n, [i[1] for i in parser.parse_batch(n.name)]) for n in batchdir.iterdir() if n.is_dir()]
    all_problems.sort(key=lambda i: len(i[1][0].goals))

    with Pool(processes) as p:
        for index, (problem_name, problems) in enumerate(tqdm(all_problems)):
            index = index + 1
            print(problem_name)

            partname = pathlib.Path(str(fname) + f".part{index}")
            if partname.exists():
                print(f"found data for part {index}")
                results[index] = read_from_file(partname, index)
                continue


            if index <= 1 or sum(1 for i in results[index - 1] if i is not None) != 0:
                sols = run_with_timeout(p, solver(), problems, 2 * 60)

                results[index] = sols
            else:
                results[index] = [None for i in range(len(problems))]


            tqdm.write(f"{bm_name} part {index}: {sols}")
            results[index] = sols

            output_data(partname, results)

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
    #             matching_strategy=MatchingStrategy.Inmatch,
    #             max_memory_usage=3 * GigaByte,
    #             debug=False,
    #             report_expansions=False,
    #         ),
    #     ),
    #     "M*"
    # ))

    files.append(run(
        lambda: EPEAStar(inmatch=True),
        "EPEA*"
    ))

    files.append(run(
        lambda: CBM(),
        "CBM"
    ))

    files.append(run(
        lambda: AStarODIDInmatch(),
        "A*-OD-ID"
    ))

    files.append(run(
        lambda: ICTSInmatching(),
        "ICTS"
    ))

    graph_results(
        *files,
        batchdir / f"{name}",
        save=True,
        bounds=False,
        legend=True,
        graph_zeros=True,
        xlabel="number of agents in a single team",
        index_mapping=lambda i: i,
        xticks=list(range(3, 24)),
        x_axis_start=3,
        title="% solved with varying number of agents",
        line_thickness=2,
    )


if __name__ == '__main__':
    main()
