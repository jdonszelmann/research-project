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


import importlib
module = sys.modules["src.main"]

# Configure algorithm
module.heuristic_type = HeuristicType.Exhaustive
module.enable_cat = True
module.enable_id = True
module.enable_sorting = True

importlib.reload(module)

modules = get_src_modules()





class AStarODID(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        return solve_with_modules(modules, solve, problem)

    @property
    def name(self) -> str:
        return "A*-OD-ID (Ivar)"
