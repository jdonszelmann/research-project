from mapfmclient import Solution, Problem, MapfBenchmarker

from python.independent import independent
from python.standard_astar import standard_astar
from python.matching_astar import matching_astar


def solve(problem: Problem) -> Solution:
    return matching_astar(problem)


if __name__ == '__main__':
    benchmarker = MapfBenchmarker(
        "5rtVuya7FkKNoU6J",
        # "R5KpjLYp54YJz2KN",
        10,
        "A* Multi agent",
        "0.0.1",
        False,
        solver=solve,
        cores=1,
        baseURL="https://mapf.nl",
        # baseURL="http://localhost:8080",
    )
    benchmarker.run()

