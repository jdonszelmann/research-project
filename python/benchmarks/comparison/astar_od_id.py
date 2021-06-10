from mapfmclient import Problem, Solution

import sys
import pathlib

from python.benchmarks.comparison.util import get_src_modules, solve_with_modules

this_dir = pathlib.Path(__file__).parent.absolute()

from python.algorithm import MapfAlgorithm

sys.path.insert(0, str(this_dir / "Astar-OD-ID"))
print(sys.path)
from src.util.grid import HeuristicType, Grid
from src.main import solve
sys.path.pop(0)

modules = get_src_modules()

# Configure algorithm
heuristic_type = HeuristicType.Exhaustive
enable_cat = True
enable_id = True
enable_sorting = True


class AStarODID(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        return solve_with_modules(modules, solve)

    @property
    def name(self) -> str:
        return "A*-OD-ID (Ivar)"
