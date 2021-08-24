import sys
import pathlib
import yaml

from python.benchmarks.comparison.util import get_src_modules, solve_with_modules

this_dir = pathlib.Path(__file__).parent.absolute()
from mapfmclient import Problem, Solution
from python.algorithm import MapfAlgorithm

sys.path.insert(0, str(this_dir / "CSE3000-RP"))
from src.env import set_env, EnvVariables
from main import solve
sys.path.pop(0)

modules = get_src_modules()


class CBM(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        def solve_cbs():
            with open(this_dir / "robbin_env.yaml") as file:
                global env_vars
                yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
                env_vars = EnvVariables(yaml_dict)
                set_env(env_vars)

            return solve(problem, False)

        a = True
        while a:
            pass

        return solve_with_modules(modules, solve_cbs)

    @property
    def name(self) -> str:
        return "CBS (Robbin)"
