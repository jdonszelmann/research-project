import csv
import logging
import glob
from typing import Callable, Tuple, Optional, Any

from collections import namedtuple
from mapfmclient import Problem, Solution
from mapfmclient.local_solver import LocalSolver
from pathlib import Path
from time import time

from src.env import get_env, CurrentSolver

ProblemResult = Tuple[str, Optional[float], Optional[int], Optional[int],
                      Optional[int], CurrentSolver]
ProblemSolution = namedtuple(
    "ProblemSolution",
    ["sol", "created_edges", "created_nodes", "amount_of_conflicts"])


def run_benchmark(solve_fn: Callable[[Problem, bool, bool], ProblemSolution]):
    env = get_env()

    data_path = Path("data")
    data_path.mkdir(parents=True, exist_ok=True)

    reset_teg = None
    disappearing_agents = False

    for root in env.benchmark.root:
        for path in sorted(glob.glob(root)):
            folder_name = path.split('/')[-1]
            reset_suffix = "" if reset_teg is None else f"_{'reset' if reset_teg else 'reuse'}"

            if glob.glob(str(data_path / f"data_{folder_name}_*")
                         ) and env.benchmark.ignore_existing:
                logging.info(f"Skipping {folder_name}")
                continue

            data_file = open(data_path /
                             f"data_{folder_name}_{time()}{reset_suffix}.csv",
                             "a",
                             newline="")
            data_writer = csv.writer(data_file)

            def new_solve(problem: Problem) -> ProblemSolution:
                return solve_fn(problem, reset_teg is True,
                                disappearing_agents)

            logging.info(f"Starting root {path}")
            for sample in range(env.benchmark.samples):
                results = LocalSolver(path, env.benchmark.cores,
                                      env.benchmark.timeout).solve(
                                          new_solve, "")

                total_solved = 0
                for problem, solution, time_seconds in results:
                    solved = solution is not None
                    total_solved += 1 if solved else 0

                    def if_solution(fn: Callable[[Solution], Any]):
                        return fn(solution) if solution is not None else None

                    result: ProblemResult = (
                        problem.id, if_solution(lambda s: time_seconds),
                        if_solution(lambda s: s.created_nodes),
                        if_solution(lambda s: s.created_edges),
                        if_solution(lambda s: s.amount_of_conflicts),
                        env.solver)
                    data_writer.writerow(result)

                logging.info(f"Total solved: {total_solved} / 200")
