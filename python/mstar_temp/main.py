from mapfmclient import MapfBenchmarker, Solution, Problem

from python.mstar_temp.heuristic import Heuristics


def solve(problem: Problem) -> Solution:
    solution = Heuristics(
        problem.grid,
        problem.starts,
        problem.goals,
        problem.width,
        problem.height,
    ).mstar_Not_OD()

    paths = [[] for _ in solution[0].identifier.actual]
    for path in solution:
        for index, coord in enumerate(path.identifier.actual):
            paths[index].append((coord.x, coord.y))

    return Solution.from_paths(paths)

def main():
    benchmarker = MapfBenchmarker(
        "5rtVuya7FkKNoU6J",
        # "R5KpjLYp54YJz2KN",
        12,
        "M*",
        "0.0.1",
        False,
        solver=solve,
        cores=1,
        baseURL="https://mapf.nl",
        # baseURL="http://localhost:8080",
    )
    benchmarker.run()

if __name__ == '__main__':
    main()