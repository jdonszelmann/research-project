
from mapfmclient import Problem, Solution

from python.algorithm import MapfAlgorithm
from python.mstar.rewrite import Config
from python.mstar.rewrite import mstar
from python.mstar.rewrite.config import MatchingStrategy

from tqdm import tqdm

import time


class ConfigurableMStar(MapfAlgorithm):
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def solve(self, problem: Problem) -> Solution:
        start = time.time()

        solution = mstar(self.cfg, problem)

        tqdm.write(f"{(time.time() - start) * 1000}ms")

        if solution is None:
            tqdm.write("no solution")
            exit()

        paths = [[] for _ in solution.path[0].identifier.actual]
        for path in solution.path:
            for index, coord in enumerate(path.identifier.actual):
                paths[index].append((coord.x, coord.y))

        return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        if self.cfg.matching_strategy == MatchingStrategy.Prematch:
            name = "prematch "
        elif self.cfg.matching_strategy == MatchingStrategy.PruningPrematch:
            name = "pruning prematch "
        elif self.cfg.matching_strategy == MatchingStrategy.SortedPruningPrematch:
            name = "sorted pruning prematch "
        elif self.cfg.matching_strategy == MatchingStrategy.Inmatch:
            name = "inmatch "
        else:
            name = "unknown matching strategy "

        if self.cfg.recursive:
            name += "rM*"
        else:
            name += "M*"

        if self.cfg.operator_decomposition:
            name += " + OD"
        if self.cfg.precompute_heuristic:
            name += " + PH"

        if self.cfg.precompute_paths:
            name += " + PP"

        if self.cfg.collision_avoidance_table:
            name += " + CAT"

        return name