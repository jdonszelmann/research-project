import time
from multiprocessing import Pool
from typing import Optional

from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem
from tqdm import tqdm

from python.algorithm import MapfAlgorithm


def run_problem_with_timeout_star(args):
    return run_problem_with_timeout(*args)


def run_problem_with_timeout(
    algorithm: MapfAlgorithm,
    problem: Problem,
    parse_maps: bool = True,
    timeout: int = 2 * 60,
) -> Optional[float]:

    start = time.time()
    try:
        if(parse_maps):
            func_timeout(
            timeout,
            algorithm.solve,
            (problem[1],),
        )
        else:
            func_timeout(
            timeout,
            algorithm.solve,
            (problem[0],),
        )
    except FunctionTimedOut:
        print("func timeout exception")
        return None
    except Exception as e:
        print("exception test")
        print(e)
        return None

    end = time.time()

    return end - start


def run_with_timeout(
    p: Pool,
    algorithm: MapfAlgorithm,
    problems: list[tuple[str,Problem]],
    parse_maps: bool = True,
    timeout: int = 2 * 60,
) -> list[Optional[float]]:

    return list(
        tqdm(
            p.imap(
                run_problem_with_timeout_star,
                [(algorithm, problem, parse_maps, timeout) for problem in problems],
            ),
            total=len(problems)
        )
    )
