from mapfmclient import MapfBenchmarker

from python.algorithm import MapfAlgorithm
from python.independent import Independent
from python.matching_astar import MatchingAStar
from python.better_matching_astar import BetterMatchingAStar
from python.mstar_solver import MStar
from python.mstar_od_solver import MStarOD
from python.visual_mstar_od_solver import VisualMStarOD
from python.prematch_mstar_solver import MStar as PrematchMStar
from python.prematch_mstar_solver_od import MStarOD as PrematchMStarOD
from python.visual_prematch_mstar_solver import MStar as VisualPrematchMStar


def submit(algorithm: MapfAlgorithm):
    benchmarker = MapfBenchmarker(
        "5rtVuya7FkKNoU6J",
        # "R5KpjLYp54YJz2KN",
        9,
        algorithm.name,
        "0.0.1",
        True,
        solver=algorithm.solve,
        cores=1,
        baseURL="https://mapf.nl",
        # baseURL="http://localhost:8080",
    )
    benchmarker.run()


if __name__ == '__main__':
    submit(PrematchMStarOD())
