import pathlib
import sys

import yaml
from mapfmclient import Problem, Solution

from python.algorithm import MapfAlgorithm

this_dir = pathlib.Path(__file__).parent.absolute()
print(sys.path)
sys.path.insert(0, str(this_dir / "src"))
from src.env import set_env, EnvVariables
from src.main import solve

sys.path.pop(0)

from python.benchmarks.comparison.util import get_src_modules, solve_with_modules

modules = get_src_modules()


class CBM(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        def solve_cbs():
            with open(this_dir / "robbin_env.yaml") as file:
                yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
                env_vars = EnvVariables(yaml_dict)
                set_env(env_vars)
            try:
                solve(problem, False, False)
            except Exception as e:
                print(e)
            return solve(problem, False, False)

        return solve_with_modules(modules, solve_cbs)

    @property
    def name(self) -> str:
        return "CBS (Robbin)"
