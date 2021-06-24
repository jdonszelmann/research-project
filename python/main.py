import pathlib as pathlib
from mapfmclient import MapfBenchmarker, ProgressiveDescriptor, BenchmarkDescriptor, Problem, MarkedLocation
import pathlib

from python.algorithm import MapfAlgorithm
from python.mstar.rewrite import Config
from python.mstar.rewrite.config import GigaByte, MatchingStrategy
from python.solvers.configurable_mstar_solver import ConfigurableMStar
from python.solvers.mstar_od_solver import MStarOD
from python.solvers.prematch_mstar_solver_od import MStarOD as PrematchMStarOD
from python.solvers.prematch_mstar_solver import MStar as PrematchMStar
from python.solvers.visual_prematch_mstar_solver import MStar as VisualPrematchMStar
from python.solvers.prematch_recursive_mstar_solver_od import RMStarOD
from python.solvers.mstar_solver import MStar
from python.solvers.better_matching_astar import BetterMatchingAStar

this_dir = pathlib.Path(__file__).parent.absolute()

with open(this_dir / ".." / "token", "r") as f:
    token = f.read()


def submit(algorithm: MapfAlgorithm):
    benchmarker = MapfBenchmarker(
        token,
        # BenchmarkDescriptor(
        #     2801,
        #     progressive_descriptor=ProgressiveDescriptor(
        #         min_agents=1,
        #         max_agents=6,
        #         num_teams=2,
        #     ),
        # ),cp5
        81,
        algorithm.name,
        algorithm.version,
        True,
        solver=algorithm.solve,
        cores=1,
        baseURL="https://mapf.nl",
    )
    benchmarker.run()


if __name__ == '__main__':
    submit(BetterMatchingAStar())
    # submit(RMStarOD())
    # submit(PrematchMStarOD())
    # submit(PrematchMStar())
    # submit(VisualPrematchMStar())
    # submit(MStar())
    # submit(MStarOD())
    # submit(ConfigurableMStar(Config(
    #     operator_decomposition=True,
    #     precompute_paths=False,
    #     precompute_heuristic=True,
    #     collision_avoidance_table=False,
    #     recursive=False,
    #     matching_strategy=MatchingStrategy.Prematch,
    #     max_memory_usage=3 * GigaByte,
    #     debug=False,
    # )))

    # m = MStar()
    # s = m.solve(Problem(
    #     grid=[[1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1], [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0], [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0], [0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0], [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0], [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0], [0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0], [1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0], [0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0], [1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1], [0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], [1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1], [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1], [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0], [0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1], [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1], [0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],
    #     width=20,
    #     height=20,
    #     starts=[MarkedLocation(x=12, y=12, color=0), MarkedLocation(x=11, y=12, color=0), MarkedLocation(x=4, y=2, color=0)],
    #     goals=[MarkedLocation(x=9, y=12, color=0), MarkedLocation(x=0, y=15, color=0), MarkedLocation(x=2, y=13, color=0)],
    # ))
    # # s = m.solve(Problem(
    # #     grid=[
    # #         [0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    # #         [1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    # #         [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    # #         [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0],
    # #         [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
    # #         [0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # #         [0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    # #         [0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0],
    # #         [0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0],
    # #         [1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    # #         [1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
    # #         [1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    # #         [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0],
    # #         [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
    # #         [0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1],
    # #         [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
    # #         [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0],
    # #         [0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    # #         [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
    # #         [1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1]
    # #     ],
    # #     width=20,
    # #     height=20,
    # #     starts=[MarkedLocation(x=19, y=13, color=0), MarkedLocation(x=1, y=16, color=0)],
    # #     goals=[MarkedLocation(x=6, y=5, color=0), MarkedLocation(x=12, y=15, color=0)],
    # # ))
    # print(s.paths)
