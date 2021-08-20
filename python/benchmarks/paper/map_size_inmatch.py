from multiprocessing import Pool
from typing import Optional, Callable

from tqdm import tqdm

from python.algorithm import MapfAlgorithm
from python.benchmarks.comparison import EPEAStar, CBM, AStarODIDInmatch
from python.benchmarks.comparison.icts import ICTS, ICTSInmatch
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
name = "map_size_25percent"
processes = 12

map_sizes = list(range(10, 105, 5))
expected_results = map_sizes
timeout = 2 * 60

def generate_maps():
    path = this_dir / name
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        pass

    dirnames = [n.name for n in path.iterdir() if n.is_dir()]

    for i in tqdm(map_sizes):

        map_generator = MapGenerator2(path)
        map_generator.generate_even_batch(
            100,  # number of maps
            i, i,  # size
            9,  # agents
            3,  # number of teams
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
    all_problems.sort(key=lambda i: i[1][0].width)

    with Pool(processes) as p:
        for index, (problem_name, problems) in enumerate(tqdm(all_problems)):
            index = index + 1
            print(problem_name)

            partname = pathlib.Path(str(fname) + f".part{index}")
            if partname.exists():
                print(f"found data for part {index}")
                results[index] = read_from_file(partname, index)
                continue

            sols = run_with_timeout(p, solver(), problems, timeout)

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

    files.append(run(
        lambda: ConfigurableMStar(
            Config(
                operator_decomposition=True,
                precompute_paths=False,
                precompute_heuristic=True,
                collision_avoidance_table=False,
                recursive=False,
                matching_strategy=MatchingStrategy.Inmatch,
                max_memory_usage=3 * GigaByte,
                debug=False,
                report_expansions=False,
            ),
        ),
        "M*"
    ))

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

    # files.append(run(
    #     lambda: ICTSInmatch(),
    #     "ICTS"
    # ))

    graph_results(
        *files,
        batchdir / f"{name}",
        save=True,
        bounds=False,
        legend=True,
        graph_zeros=True,
        xlabel="map size (n x n)",
        index_mapping=lambda i: map_sizes[i-1],
        x_axis_start=10,
        title="% solved with varying team sizes",
        line_thickness=2,
    )


if __name__ == '__main__':
    main()
