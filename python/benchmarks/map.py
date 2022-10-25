import os
import random
from multiprocessing import Pool
from numbers import Number
from queue import Queue
from random import randint, uniform
from typing import List, Tuple

from mapfmclient import Problem, MarkedLocation
from tqdm import tqdm

from python.coord import Coord

processes = 12


class MapGenerator:

    def __init__(self, map_root):
        self.map_root = map_root

    def generate_map(self, width: int,
                     height: int,
                     num_agents: List[int],
                     open_factor: float = 0.75,
                     max_neighbors: int = 1,
                     min_goal_distance: float = 0.5,
                     max_goal_distance: float = 1,
                     file=None
                     ) -> Problem:
        while True:
            if not file:
                grid = self.generate_maze(width, height, open_factor=open_factor, max_neighbors=max_neighbors)
            else:
                with open(file) as f:
                    grid = []
                    for line in f.read().splitlines():
                        row = []
                        for value in line:
                            if value == '@':
                                row.append(1)
                            else:
                                row.append(0)
                        grid.append(row)
            count_traversable = 0
            for y in range(height):
                count_traversable += width - sum(grid[y])
            if count_traversable < (open_factor * width * height * 0.25 * max_neighbors) or self.__num_3neighbors(grid) < sum(
                    num_agents) - 1:
                tqdm.write("Not enough traversable cells or not solvable, running again!")
            else:
                result = None
                while result is None:
                    try:
                        # connect
                        result = self.__generate_agent_positions(grid, width, height, num_agents, min_goal_distance, max_goal_distance)
                    except:
                        pass
                starts, goals = result
                start_locations: List[MarkedLocation] = []
                goal_locations: List[MarkedLocation] = []

                i = 0
                for color, team_size in enumerate(num_agents):
                    for _ in range(team_size):
                        start_locations.append(MarkedLocation(color, starts[i].x, starts[i].y))
                        goal_locations.append(MarkedLocation(color, goals[i].x, goals[i].y))
                        i += 1
                return Problem(width=width, height=height, grid=grid, starts=start_locations, goals=goal_locations)

    def generate_map_file(self, name, width: int,
                          height: int,
                          num_agents: List[int],
                          open_factor: float = 0.75,
                          max_neighbors: int = 1,
                          min_goal_distance: float = 0.5,
                          max_goal_distance: float = 1,
                          file=None):
        problem = self.generate_map(width, height, num_agents, open_factor, max_neighbors, min_goal_distance, max_goal_distance, file)
        self.__store_map(name, problem)

    def generate_even_batch(self,
                            amount: int,
                            width: int,
                            height: int,
                            agents: int,
                            teams: int,
                            prefix="",
                            package_name: str = None,
                            file_name: str = None,
                            open_factor: float = 0.75,
                            max_neighbors: int = 1,
                            min_goal_distance: float = 0.5,
                            max_goal_distance: float = 1,
                            file=None
                            ):
        package_name = package_name if package_name is not None else f"{prefix}-{width}x{height}-A{agents}_T{teams}"
        file_name = package_name if file_name is None else file_name
        min_team_count = int(agents/teams)
        diff = agents - (min_team_count * teams)
        num_agents = [min_team_count for _ in range(teams)]
        os.mkdir(os.path.join(self.map_root, package_name))
        for i in range(diff):
            num_agents[i] += 1

        actions = []
        for i in range(amount):
            if i < 10 < amount:
                i = f"0{i}"
            if int(i) < 100 < amount:
                i = f"0{i}"
            name = os.path.join(package_name, f"{file_name}-{i}")
            actions.append((name, width, height, num_agents, open_factor, max_neighbors, min_goal_distance, max_goal_distance, file))

        with Pool(processes) as p:
            p.starmap(self.generate_map_file, actions)

    def __generate_agent_positions(self, grid, width, height, num_agents: List[int],
                                   min_distance: float,
                                   max_distance: float) -> Tuple[List[Coord], List[Coord]]:
        agent_positions = []
        goal_positions = []

        # Find a random position for each agent
        for x in range(sum(num_agents)):
            start_x = randint(0, width - 1)
            start_y = randint(0, height - 1)
            while grid[start_y][start_x] != 0 or Coord(start_x, start_y) in agent_positions:
                start_x = randint(0, width - 1)
                start_y = randint(0, height - 1)

            agent_positions.append(Coord(start_x, start_y))

        for agent in agent_positions:
            queue = Queue()
            queue.put((agent, 0))
            distances, m = self.__compute_heuristic(queue, grid)
            distance = random.randint(int(m * min_distance), int(m * max_distance))
            possible_locations = []
            for y, row in enumerate(distances):
                for x, value in enumerate(row):
                    if value == distance and Coord(x, y) not in goal_positions:
                        possible_locations.append(Coord(x, y))

            goal_positions.append(random.choice(possible_locations))

        return agent_positions, goal_positions

    @staticmethod
    def __num_3neighbors(grid: List[List[int]]) -> int:
        height = len(grid)
        width = len(grid[0])
        res = 0
        for y in range(height):
            for x in range(width):
                count = 0
                for ndx, ndy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    neighbor_x = x + ndx
                    neighbor_y = y + ndy
                    if 0 <= neighbor_x < width and 0 <= neighbor_y < height and grid[neighbor_y][neighbor_x] == 0:
                        count += 1
                if count == 3:
                    res += 1
        return res

    def __compute_heuristic(self, queue: Queue, grid: List[List[int]]) -> Tuple[List[List[Number]], int]:
        visited = set()
        heuristic = [[float('inf') for _ in range(len(grid[0]))] for _ in range(len(grid))]
        m = 0
        while not queue.empty():
            coord, dist = queue.get()
            m = max(dist, m)
            if coord in visited:
                continue
            visited.add(coord)

            # Already has a better distance
            if heuristic[coord.y][coord.x] != float("inf"):
                continue
            heuristic[coord.y][coord.x] = dist

            for neighbor in self.__get_neighbors(grid, coord):
                if neighbor not in visited:
                    queue.put((neighbor, dist + 1))
        return heuristic, m

    @staticmethod
    def __get_neighbors(grid: List[List[int]], coords: Coord):
        res = list()
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            new_coord = coords + Coord(dx, dy)
            if 0 <= new_coord.y < len(grid) and 0 <= new_coord.x < len(grid[0]) and grid[new_coord.y][new_coord.x] == 0:
                res.append(new_coord)
        return res

    @staticmethod
    def generate_maze(width: int, height: int, open_factor: float, max_neighbors: int) -> List[List[int]]:
        grid: List[List[int]] = []
        for x in range(height):
            grid.append([1] * width)

        start_x = randint(0, width - 1)
        start_y = randint(0, height - 1)

        grid[start_y][start_x] = 0

        frontier = [Coord(start_x, start_y)]

        while frontier:
            pos = frontier.pop()
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                if uniform(0, 1) < open_factor:
                    new_x = pos.x + dx
                    new_y = pos.y + dy

                    # Check if not out of bounds and if not already opened
                    if 0 <= new_x < width and 0 <= new_y < height and grid[new_y][new_x] != 0:
                        # Check number of open neighbors
                        count = 0
                        for ndx, ndy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                            neighbor_x = new_x + ndx
                            neighbor_y = new_y + ndy
                            if 0 <= neighbor_x < width and 0 <= neighbor_y < height and grid[neighbor_y][
                                neighbor_x] == 0:
                                count += 1
                        if count <= max_neighbors:
                            grid[new_y][new_x] = 0
                            frontier.append(Coord(new_x, new_y))
        return grid

    def __store_map(self, name: str, problem: Problem):
        file_path = os.path.join(self.map_root, name + ".map")
        with open(file_path, 'w') as f:
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
