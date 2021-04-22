from mapfmclient import Solution, Problem, MapfBenchmarker

from python.independent import independent
from python.standard_astar import standard_astar


def solve(problem: Problem) -> Solution:
    return standard_astar(problem)


if __name__ == '__main__':
    benchmarker = MapfBenchmarker(
        "5rtVuya7FkKNoU6J",
        # "R5KpjLYp54YJz2KN",
        3,
        "A* Multi agent",
        "0.0.1",
        True,
        solver=solve,
        cores=1,
        baseURL="https://mapf.nl",
        # baseURL="http://localhost:8080",
    )
    benchmarker.run()

