import time
from multiprocessing import Pool
from typing import Optional

from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem
from tqdm import tqdm

from python.algorithm import MapfAlgorithm


def run_problem_with_timeout_expansion_star(args):
    return run_problem_with_expansion_timeout(*args)


def run_problem_with_expansion_timeout(
    algorithm: MapfAlgorithm,
    problem: Problem,
    timeout: int = 2 * 60,
) -> Optional[list[int]]:

    start = time.time()
    try:
        func_timeout(
            timeout,
            algorithm.solve,
            (problem,),
        )
    except FunctionTimedOut:
        return None
    except Exception as e:
        print(e)
        return None

    end = time.time()

    return algorithm.cfg.expansions


def run_with_expansion_timeout(
    p: Pool,
    algorithm: MapfAlgorithm,
    problems: list[Problem],
    timeout: int = 2 * 60,
) -> list[Optional[list[int]]]:

    return list(
        tqdm(
            p.imap(
                run_problem_with_timeout_expansion_star,
                [(algorithm, problem, timeout) for problem in problems],
            ),
            total=len(problems)
        )
    )
