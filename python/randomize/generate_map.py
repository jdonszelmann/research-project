import enum
import functools
import random
from collections import deque, defaultdict
from itertools import repeat, count
from multiprocessing import Pool
from numbers import Number
from random import randint, uniform
from typing import Iterator, Optional, Union

import sys

from func_timeout import func_timeout, FunctionTimedOut
from tqdm import tqdm

from python.algorithm import MapfAlgorithm
from python.solvers import *
from python.coord import Coord
from math import inf


import copy
import matplotlib.pyplot as plt

from mapfmclient import Problem, MarkedLocation


# sys.setrecursionlimit(10_000)

class Direction(enum.Enum):
    North = 1
    East = 2
    South = 3
    West = 4

    @property
    def value(self) -> tuple[int, int]:
        if self == Direction.North:
            return 0, 1
        elif self == Direction.East:
            return 1, 0
        elif self == Direction.South:
            return 0, -1
        elif self == Direction.West:
            return -1, 0
        else:
            raise ValueError("invalid enum value")

    def coord(self) -> Coord:
        return Coord(*self.value)


def map_printer(grid: list[list[int]]):
    print('██' * (len(grid[0]) + 2))
    for y in range(len(grid)):
        print('██' + ''.join(['  ' if pos == 0 else '██' for pos in grid[y]]) + '██')
    print('██' * (len(grid[0]) + 2))


def generate_map(width: int,
                 height: int,
                 num_agents: list[int],
                 open_factor: float = 0.75,
                 max_neighbors: int = 1,
                 min_goal_distance: float = 0.5,
                 max_goal_distance: float = 1
                 ) -> Problem:
    while True:
        grid = generate_maze(width, height, open_factor=open_factor, max_neighbors=max_neighbors)
        count_traversable = 0
        for y in range(height):
            count_traversable += width - sum(grid[y])
        if count_traversable < (open_factor * width * height * 0.25 * max_neighbors) or num_3neighbors(grid) < sum(num_agents) - 1:
            pass
            # print("Not enough traversable cells or not solvable, running again!")
        else:
            starts, goals = generate_agent_positions(
                grid,
                width, height,
                num_agents,
                min_goal_distance, max_goal_distance
            )
            start_locations: list[MarkedLocation] = []
            goal_locations: list[MarkedLocation] = []


            i = 0
            for color, team_size in enumerate(num_agents):
                for _ in range(team_size):
                    start_locations.append(MarkedLocation(color, starts[i].x, starts[i].y))
                    goal_locations.append(MarkedLocation(color, goals[i].x, goals[i].y))
                    i += 1

            random.shuffle(goal_locations)

            return Problem(width=width, height=height, grid=grid, starts=start_locations, goals=goal_locations)


def generate_agent_positions(grid,
                             width: int,
                             height: int,
                             num_agents: list[int],
                             min_distance: float,
                             max_distance: float) -> tuple[list[Coord], list[Coord]]:
    agent_positions = []
    goal_positions = []

    # Find a random position for each agent
    for x in range(sum(num_agents)):
        start_x = randint(0, width - 1)
        start_y = randint(0, height - 1)
        while grid[start_y][start_x] != 0 and Coord(start_x, start_y) not in agent_positions:
            start_x = randint(0, width - 1)
            start_y = randint(0, height - 1)

        agent_positions.append(Coord(start_x, start_y))

    for agent in agent_positions:
        queue = deque()
        queue.append((agent, 0))
        distances, m = compute_heuristic(queue, grid)
        possible_locations = []
        while len(possible_locations) == 0:
            distance = random.randint(int(m * min_distance), int(m * max_distance))
            for y, row in enumerate(distances):
                for x, value in enumerate(row):
                    if value == distance and (c := Coord(x, y)) not in goal_positions:
                        possible_locations.append(c)

        goal_positions.append(random.choice(possible_locations))

    return agent_positions, goal_positions


def num_3neighbors(grid: list[list[int]]) -> int:
    height = len(grid)
    width = len(grid[0])
    res = 0
    for y in range(height):
        for x in range(width):
            count = 0
            for neighbor in Direction:
                ndx, ndy = neighbor.value
                neighbor_x = x + ndx
                neighbor_y = y + ndy
                if 0 <= neighbor_x < width and 0 <= neighbor_y < height and grid[neighbor_y][neighbor_x] == 0:
                    count += 1
            if count == 3:
                res += 1
    return res


def compute_heuristic(queue: deque, grid: list[list[int]]) -> tuple[list[list[Number]], int]:
    visited = set()
    heuristic = [[inf for _ in grid[0]] for _ in grid]
    m = 0
    while len(queue) > 0:
        coord, dist = queue.popleft()
        m = max(dist, m)
        if coord in visited:
            continue
        visited.add(coord)

        # Already has a better distance
        if heuristic[coord.y][coord.x] != inf:
            continue
        heuristic[coord.y][coord.x] = dist

        for neighbor in get_neighbors(grid, coord):
            if neighbor not in visited:
                queue.append((neighbor, dist + 1))
    return heuristic, m


def get_neighbors(grid: list[list[int]], coords: Coord) -> Iterator[Coord]:
    return (
        coords + d.coord()
        for d in Direction
        if (lambda new_coord:
            0 <= new_coord.y < len(grid) and
            0 <= new_coord.x < len(grid[0]) and
            grid[new_coord.y][new_coord.x] == 0
            )(coords + d.coord())
    )


def generate_maze(width: int, height: int, open_factor: float, max_neighbors: int) -> list[list[int]]:
    grid: list[list[int]] = []
    for x in range(height):
        grid.append([1] * width)

    start_x = randint(0, width - 1)
    start_y = randint(0, height - 1)

    grid[start_y][start_x] = 0

    frontier = [Coord(start_x, start_y)]

    while frontier:
        pos = frontier.pop()
        for d in Direction:
            if uniform(0, 1) < open_factor:
                dx, dy = d.value
                new_x = pos.x + dx
                new_y = pos.y + dy

                # Check if not out of bounds and if not already opened
                if 0 <= new_x < width and 0 <= new_y < height and grid[new_y][new_x] != 0:
                    # Check number of open neighbors
                    count = 0
                    for neighbor in Direction:
                        ndx, ndy = neighbor.value
                        neighbor_x = new_x + ndx
                        neighbor_y = new_y + ndy
                        if 0 <= neighbor_x < width and 0 <= neighbor_y < height and grid[neighbor_y][neighbor_x] == 0:
                            count += 1
                    if count <= max_neighbors:
                        grid[new_y][new_x] = 0
                        frontier.append(Coord(new_x, new_y))
    return grid


def store_map(name: str, folder: str, problem: Problem):
    with open(f'../../maps/{folder}/{name}.map', 'w') as f:
        f.write(f'width {problem.width}\n')
        f.write(f'height {problem.height}\n')

        # Grid
        for row in problem.grid:
            f.write(''.join(map(lambda x: '.' if x == 0 else '@', row)) + "\n")

        # Number of agents
        f.write(f'{len(problem.starts)}\n')
        # Starts
        for start in problem.starts:
            f.write(f'{start.x} {start.y} {start.color}\n')
        f.write('\n')

        for goal in problem.goals:
            f.write(f'{goal.x} {goal.y} {goal.color}\n')


def generate_batch(name: str,
                   folder: str,
                   amount: Union[int, float],
                   width: int,
                   height: int,
                   num_agents: list[int],
                   open_factor: float = 0.75,
                   max_neighbors: int = 2,
                   min_goal_distance: float = 0.5,
                   max_goal_distance: float = 1,
                   yield_problem: bool = False
                   ) -> Optional[Iterator[Problem]]:
    processes = 12
    batch_size = processes * 10

    if type(amount) == float:
        if amount == inf:
            iterator = iter(int, 1)
        else:
            iterator = range(int(amount / batch_size))
    else:
        iterator = range(int(amount / batch_size))

    print(f"generating with open_factor={open_factor} and max_neighbours={max_neighbors}")
    with Pool(processes) as p:
        with tqdm(total=amount) as pbar:
            for i in iterator:
                results = p.starmap(
                    generate_map,
                    repeat((
                        width,
                        height,
                        num_agents,
                        open_factor,
                        max_neighbors,
                        min_goal_distance,
                        max_goal_distance
                    ), batch_size)
                )
                pbar.update(batch_size)
                for problem in results:
                    filename = f'{name}-{i}'
                    if yield_problem:
                        yield problem
                    else:
                        store_map(filename, folder, problem)


colors = [
    (204, 68, 82),
    (36, 97, 128),
    (128, 29, 39),
    (47, 152, 204),
    (17, 128, 42),
    (67, 204, 98),
    (57, 204, 174),
    (102, 82, 74),
    (128, 124, 23),
    (204, 111, 78),
]


def solve_problem_with_timeout(algorithm: MapfAlgorithm, problem: Problem, index: int) -> bool:
    if index % 100 == 0:
        print(f"\r{index}", end="")
    try:
        func_timeout(
            30,
            algorithm.solve,
            (problem,),
        )
    except FunctionTimedOut:
        return False
    except Exception as e:
        print(e)
        pass
    return True


def one_solver(algorithm, problems: list[Problem]):
    print(f"running {algorithm.name} with {param} agents")
    with Pool(12) as p:
        res: list[bool] = p.starmap(
            solve_problem_with_timeout,
            zip(
                repeat(algorithm),
                problems,
                [i for i in range(len(problems))],
            )
        )
        print("\r", end="")

        return res.count(True)


def run_test(param):
    solvers = [
        # MStar(),
        # MStarOD(),
        PrematchMStarOD(),
        PrematchMStar(),
        # BetterMatchingAStar(),
    ]

    m = 500
    problems = list(
        generate_batch('test', 'test',
                       amount=m,
                       width=20,
                       height=20,
                       num_agents=param,  # Team of 2 agents and a team of 3 agents
                       yield_problem=True,
                       )
    )


    return [
        (solver.name, one_solver(solver, problems) / m)
        for solver in solvers
    ]


if __name__ == '__main__':
    # maze = generate_maze(
    #     20, 20,
    #     open_factor=0.75,
    #     max_neighbors=2,
    # )
    # map_printer(maze)
    # exit()

    params = [
        [1],
        # [2],
        # [3],
        # [4],
        # [5],
        # [6],
        # [7],
        # [8],
    ]

    data = defaultdict(lambda: ([], []))

    data["prematch M*"] = ([1, 2, 3, 4, 5, 6], [0.96, 0.96, 0.891, 0.443, 0.129, 0.024])
    data["prematch M* + OD"] = ([1, 2, 3, 4, 5, 6], [0.96, 0.96, 0.851, 0.483, 0.176, 0.032])
    data["M*"] = ([1, 2, 3, 4, 5, 6], [0.96, 0.96, 0.169, 0.041, 0.0, 0.0])
    data["A*"] = ([1, 2, 3, 4, 5, 6], [0.96, 0.96, 0.01, 0.00, 0.00, 0.0])

    # data["prematch M*"] = ([1, 2, 3, 4, 5, 6, 7, 8], [0.96, 0.96, 0.96, 0.936, 0.798, 0.438, 0.124, 0.026])
    # data["prematch M* + OD"] = ([1, 2, 3, 4, 5, 6, 7, 8], [0.96, 0.96, 0.96, 0.94, 0.872, 0.63, 0.276, 0.096])
    # data["M*"] = ([1, 2, 3, 4, 5, 6, 7, 8], [0.96, 0.954, 0.208, 0.03, 0.0, 0.0, 0.0, 0.0])
    # data["A*"] = ([1, 2, 3, 4, 5, 6, 7, 8], [0.96, 0.308, 0.002, 0.0, 0.0, 0.0, 0.0, 0.0])

    for param in params:
        # result = run_test(param)
        #
        # for i in result:
        #     name, dp = i
        #     data[name][0].append(param[0])
        #     data[name][1].append(dp)

        print(data)
        plt.style.use('seaborn-whitegrid')
        plt.rcParams['axes.facecolor'] = '#F9E4AD'
        plt.rcParams['axes.edgecolor'] = '#000000'
        plt.rcParams['figure.facecolor'] = '#F9E4AD'
        plt.rcParams['font.size'] = '14'
        plt.grid(color='#a0a0a0', linestyle='-', linewidth=0.7)
        plt.title("3/4 filled in map")
        plt.ylabel("% solved in 30 seconds")
        plt.xlabel("number of agents")
        plt.xticks([i for i in range(1, 12)])
        # plt.xlim(1, 10)
        for (name, dp), color in zip(copy.deepcopy(dict(data)).items(), colors):
            if len(data[0]) != 0 and type(name) == str:
                plt.plot(
                    dp[0],
                    [i * (1/0.96) * 100 for i in dp[1]],
                    color=f"#{hex(color[0])[2:]}{hex(color[1])[2:]}{hex(color[2])[2:]}",
                    label=name,
                    linewidth=3
                )

        plt.legend()
        plt.show()

"""
[
    [0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0],
    [1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
    [1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1]
]
[MarkedLocation(19, 13, color=0), MarkedLocation(1, 16, color=0)]
[MarkedLocation(6, 5, color=0), MarkedLocation(12, 15, color=0)]
"""