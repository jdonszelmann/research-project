import re

from mapfmclient import Problem as cProblem, Solution
import subprocess
import yaml
from mapfmclient import Problem as cProblem, Solution

from python.algorithm import MapfAlgorithm

# cbs_path = "/home/jesse/Documents/GitProjects/CBS/CBSH2-RTC-main/cbs"
cbs_ta_path = "/home//jeroendijk/BCP-paper/python/benchmarks/comparison/cbs-ta/cbs_ta"


class CBSSolver(MapfAlgorithm):
    def solve(self, problem: cProblem) -> Solution:
        # print("Starts: ", problem.starts)
        # print("Goals: ", problem.goals)
        # print("Grid: ", problem.grid)
        # print("width, height: ", problem.width, problem.height)

        map_path = "temp/" + problem.name
        num_of_agents = len(problem.starts)
        obstacles = []
        for h in range(problem.height):
            for w in range(problem.width):
                if problem.grid[h][w] == 1:
                    obstacles.append(list((w,h)))
        goals = [[] for _ in range(num_of_agents)]
        for goal in problem.goals:
            goals[goal.color].append((goal.x, goal.y))
        scenario_path = map_path.replace(".map", ".yaml")
        f = open(scenario_path, 'w')
        f.write("map:\n")
        f.write("  dimensions: {}\n".format([problem.width, problem.height]))
        f.write("  obstacles:\n")
        for o in obstacles:
            f.write("    - {}\n".format(list(o)))
        f.write("agents:\n")
        for i in range(num_of_agents):
            start = [problem.starts[i].x, problem.starts[i].y]
            goal = goals[problem.starts[i].color]
            f.write("""  - name: agent{}
    start: {}\n""".format(i, start))
            f.write("    potentialGoals:\n")
            for g in goal:
                f.write("      - {}".format(list(g)))
                f.write("\n")
        f.close()

        args = [cbs_ta_path, "-i", scenario_path, "-o", "output.yaml"]
        try:
            subprocess.run(args, timeout=problem.timeout,
                       stdout=subprocess.DEVNULL)  # .returncode , stdout=subprocess.DEVNULL
        except Exception as e:
            print(e)

        with open("output.yaml") as output_file:
            return yaml.safe_load(output_file)["statistics"]["cost"]

    @property
    def name(self) -> str:
        return "CBS-TA"