import logging
import subprocess
from datetime import datetime
from typing import Type, Union

from mapfmclient import MapfBenchmarker, Problem, Solution

from python.benchmarks.comparison.src.benchmark import run_benchmark, ProblemSolution
from python.benchmarks.comparison.src.cbm.cbm_graph import GraphManager
from python.benchmarks.comparison.src.cbm.ssp.cbm_ssp_solver import CBMSSPSolver
from python.benchmarks.comparison.src.debug.constraint_tree import ConstraintTree
from python.benchmarks.comparison.src.debug.debug import load_intermediate_solution
from python.benchmarks.comparison.src.debug.profiling import profile
from python.benchmarks.comparison.src.env import load_env, get_env
from python.benchmarks.comparison.src.solver import Solver


def get_solver() -> Type[Solver]:
    return CBMSSPSolver


def solve(problem: Problem, reset_teg: bool,
          disappearing_agents: bool) -> Union[Solution, ProblemSolution]:
    solution = load_intermediate_solution()

    solver = get_solver()
    grid = solver.Grid(problem)

    if solution is None:
        low_level_solver = solver.LowLevelSolver(grid, reset_teg,
                                                 disappearing_agents)
        high_level_solver = solver.HighLevelSolver(low_level_solver, problem)

        constraint_tree = ConstraintTree(0, None)
        root = solver.CTNode(set(), constraint_tree)

        solution = high_level_solver.solve(root)

    if get_env().run_benchmark:
        solution = ProblemSolution(solution.to_mapfm_solution(grid, problem),
                                   GraphManager.created_edges,
                                   GraphManager.created_nodes,
                                   solution.amount_of_conflicts)
        GraphManager.created_edges = 0
        GraphManager.created_nodes = 0
        return solution
    else:
        return solution.to_mapfm_solution(grid, problem)


def get_version() -> str:
    git_hash = subprocess.check_output(["git", "describe",
                                        "--always"]).strip().decode()
    is_dirty = subprocess.check_output(["git", "diff",
                                        "HEAD"]).strip().decode()
    return f"{'D_' if is_dirty else ''}{git_hash}"


class DeltaTimeFormatter(logging.Formatter):
    def format(self, record):
        duration = datetime.utcfromtimestamp(record.relativeCreated / 1000)
        record.delta = duration.strftime("%H:%M:%S:%f")[:-3]
        return super().format(record)


if __name__ == '__main__':
    # Load env vars
    load_env()
    env = get_env()

    # Setup logging
    log_format = "\033[94m[%(delta)s]\033[90m %(message)s"
    fmt = DeltaTimeFormatter(log_format)

    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    logging.getLogger().addHandler(handler)

    logging.getLogger().setLevel(env.debug.print_level)


    def solve_fn(problem: Problem,
                 reset_teg: bool = False,
                 disappearing_agents: bool = True):
        if get_env().debug.profile:
            return profile(solve, problem, reset_teg, disappearing_agents)
        return solve(problem, reset_teg, disappearing_agents)


    if env.run_benchmark:
        run_benchmark(solve_fn)
    else:
        version = get_version()
        benchmark = MapfBenchmarker(token=env.server_problem.api_token,
                                    benchmark=env.server_problem.id,
                                    algorithm=get_solver().get_name(),
                                    version=version,
                                    debug=env.server_problem.debug,
                                    solver=solve_fn,
                                    cores=1,
                                    baseURL=env.server_problem.base_url)

        benchmark.run()
