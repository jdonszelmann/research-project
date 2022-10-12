import subprocess
import re

from mapf_branch_and_bound.bbsolver import solve_bb
from mapfmclient import Problem as cProblem, Solution

from python.algorithm import MapfAlgorithm

# cbs_path = "/home/jesse/Documents/GitProjects/CBS/CBSH2-RTC-main/cbs"
cbs_path = "/data/BCP-paper/python/benchmarks/comparison/cbs-prematch/cbs-prematch"


class CBSSolver(MapfAlgorithm):
    def solve(self, problem: cProblem) -> Solution:
        res = solve_bb(problem, self.solve_internal)
        return res

    def solve_internal(self, problem: cProblem, bound) -> Solution:
        version_info = "version 1"
        map_path = "temp/" + problem.name
        num_of_agents = len(problem.starts)

        scenario_path = map_path.replace(".map", ".scen")
        with open(scenario_path, "w") as f:
            f.write(version_info + "\n")
            for i, start in enumerate(problem.starts):
                c = start.color
                sx = start.x
                sy = start.y
                for goal in problem.goals:
                    if goal.color == c:
                        gx = goal.x
                        gy = goal.y
                f.write(
                    "{}\ttemp.map\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(i, problem.height, problem.width, sx, sy, gx,
                                                                        gy, i))

        with open(map_path, "w") as f:
            f.write("type octile\nheight {}\nwidth {}\nmap\n".format(problem.height, problem.width))
            for line in problem.grid:
                for cell in line:
                    f.write("@" if cell else ".")
                f.write("\n")

        args = [cbs_path, "-m", map_path]
        args += ["-a", scenario_path]
        args += ["-t", str(problem.timeout * 2)]
        args += ["--outputPaths=paths.txt"]
        args += ["-k", str(num_of_agents)]
        if bound is not None:
            args += ["-u", str(bound)]  # + len(problem.starts)
        subprocess.run(args, timeout=problem.timeout, stdout=subprocess.DEVNULL)  # .returncode , stdout=subprocess.DEVNULL

        paths = []

        with open("paths.txt", "r") as f:
            re_p = re.compile("(\(\d+,\d+\))")
            while True:
                line = f.readline()
                if not line: break
                path = []
                for node in re_p.findall(line):
                    node = node.replace("(", "").replace(")", "")
                    x, y = node.split(",")
                    path.append((int(x), int(y)))
                paths.append(path)
        return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "CBS-MAPFM-Prematch"
