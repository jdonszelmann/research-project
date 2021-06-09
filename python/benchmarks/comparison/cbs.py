
import sys
import pathlib
import yaml

this_dir = pathlib.Path(__file__).parent.absolute()
from mapfmclient import Problem, Solution
from python.algorithm import MapfAlgorithm


sys.path.insert(0, str(this_dir / "CSE3000-RP"))
from src.env import set_env, EnvVariables
from main import solve
sys.path.pop(0)

modules = sys.modules
srcs = []
for i in sys.modules:
    if "src" in i:
        srcs.append(i)
for i in srcs:
    del sys.modules[i]



class CBS(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        old = sys.modules
        sys.modules = modules
        with open(this_dir / "robbin_env.yaml") as file:
            global env_vars
            yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
            env_vars = EnvVariables(yaml_dict)
            set_env(env_vars)


        res = solve(problem, False)
        sys.modules = old
        return res

    @property
    def name(self) -> str:
        return "CBS (Robbin)"