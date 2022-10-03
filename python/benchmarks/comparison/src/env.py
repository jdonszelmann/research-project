from __future__ import annotations

from enum import Enum

import yaml
from pathlib import Path

from typing import Optional

env_vars: EnvVariables = None


class ServerProblemVariables:
    def __init__(self, yaml_dict):
        self.id = yaml_dict["id"]
        self.debug = bool(yaml_dict["debug"])
        self.base_url = str(yaml_dict["base-url"])
        self.api_token = str(yaml_dict["api-token"])
        self.cores = int(yaml_dict["cores"])


class BenchmarkVariables:
    def __init__(self, yaml_dict):
        self.root = yaml_dict["root"]
        self.samples = int(yaml_dict["samples"])
        self.cores = int(yaml_dict["cores"])
        self.ignore_existing = bool(yaml_dict["ignore-existing"])

        timeout = int(yaml_dict["timeout"])
        self.timeout: Optional[int] = None if timeout == -1 else timeout


class IntermediateVariables:
    def __init__(self, yaml_dict):
        self.save = bool(yaml_dict["save"])
        self.load_path = str(yaml_dict["load_path"])


class DebugVariables:
    def __init__(self, yaml_dict):
        self.ct_visualize = bool(yaml_dict["ct-visualize"])
        self.nf_visualize = bool(yaml_dict["nf-visualize"])
        self.output_solution = bool(yaml_dict["output-solution"])
        self.profile = bool(yaml_dict["profile"])

        self.print_level = yaml_dict["print-level"]
        self.print_memory = bool(yaml_dict["print-memory"])

        self.intermediates = IntermediateVariables(yaml_dict["intermediates"])


class CurrentSolver(Enum):
    SSP = 0
    ILP = 1
    SSP_ILP = 2
    ASTAR = 3
    SSP_RESET = 4

    def __str__(self):
        if self == CurrentSolver.SSP:
            return "SSP"
        elif self == CurrentSolver.SSP_ILP:
            return "ILP"
        elif self == CurrentSolver.ILP:
            return "-"
        elif self == CurrentSolver.SSP_RESET:
            return "SSP w/o re-use"
        elif self == CurrentSolver.ASTAR:
            return "CBS"


class EnvVariables:
    def __init__(self, yaml_dict):
        self.solver = CurrentSolver[yaml_dict["solver"]]
        self.run_benchmark = bool(yaml_dict["run-benchmark"])

        self.server_problem = ServerProblemVariables(
            yaml_dict["server-problem"])
        self.benchmark = BenchmarkVariables(yaml_dict["benchmark"])

        self.debug = DebugVariables(yaml_dict["debug"])


def set_env(env: EnvVariables):
    global env_vars
    env_vars = env


def load_env():
    with open(Path(__file__).parent / "env.yaml") as file:
        global env_vars
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
        env_vars = EnvVariables(yaml_dict)


def get_env() -> EnvVariables:
    return env_vars
