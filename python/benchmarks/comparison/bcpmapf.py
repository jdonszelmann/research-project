from mapfmclient import MapfBenchmarker, ProgressiveDescriptor, BenchmarkDescriptor, MarkedLocation, Problem as cProblem, Solution
from python.algorithm import MapfAlgorithm
import subprocess
import os
import re

#bcp_mapf_path = "/home/jessemulderij/bcp-mapf/build/bcp-mapf"
bcp_mapf_path = "/home/jesse/Documents/GitProjects/bcp-mapf/build/bcp-mapf"

class BCPSolver(MapfAlgorithm):

    
    def solve(self, problem: cProblem) -> Solution:
        # print("Starts: ", problem.starts)
        # print("Goals: ", problem.goals)
        # print("Grid: ", problem.grid)
        # print("width, height: ", problem.width, problem.height)
        version_info = "version 1 graph"
        map_path = "temp/" + problem.name
        #map_path = "temp.map"
        num_of_agents = len(problem.starts)

        types = {}
        starts = []
        goals = []
        for i, start in enumerate(problem.starts):
            x = start.x
            y = start.y
            c = start.color
            start_node = "({},{})".format(x,y)
            starts.append(start_node)
            if not c in types: types[c] = []
            types[c].append(i)
        for i, goal in enumerate(problem.goals):
            x = goal.x
            y = goal.y
            c = goal.color
            goal_node = "({},{})".format(x,y)
            goals.append((goal_node, c))

        scenario_path = map_path.replace(".map", ".scen")
        #scenario_path = "temp.scen"
        with open(scenario_path, "w") as f:
            f.write(version_info + "\n")
            f.write(problem.name + "\n")
            f.write("Num_of_Agents {}\n".format(num_of_agents))
            f.write("types\n")
            for key, val in types.items():
                f.write("{} {}\n".format(key, " ".join([str(v) for v in val])))
            f.write("agents starts\n")
            for i, start in enumerate(starts):
                f.write("{} {}\n".format(i, start))
            f.write("goals\n")
            for goal in goals:
                f.write("{} {}\n".format(goal[1], goal[0]))
            f.close()

        with open(map_path, "w") as f:
            f.write("type octile\nheight {}\nwidth {}\nmap\n".format(problem.height, problem.width))
            for line in problem.grid:
                for cell in line:
                    f.write("@" if cell else ".")
                f.write("\n")
            f.close()

        print(scenario_path)
        print(map_path)

        #subprocess.run([bcp_mapf_path, "-f", os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp.scen")])

        exitvalue = subprocess.run([bcp_mapf_path, "-f", scenario_path], timeout = problem.timeout, stdout=subprocess.DEVNULL).returncode
        print(str(exitvalue))

        paths = []
        # with open("/home/jesse/Documents/GitProjects/bcp-mapf/build/outputs/temp.sol", "r") as f:
        #     sol_val = int(f.readline())
        #     f.readline()
        #     re_p = re.compile("(\(\d+,\d+\))")
        #     while True:
        #         line = f.readline()
        #         if not line: break
        #         path = []
        #         for node in re_p.findall(line):
        #             node = node.replace("(", "").replace(")","")
        #             x,y = node.split(",")
        #             path.append((int(x),int(y)))
        #         paths.append(path)
        #     #print(paths)
                    
        # print(Solution.from_paths(paths).serialize())   	
        return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "BCP-MAPFM"