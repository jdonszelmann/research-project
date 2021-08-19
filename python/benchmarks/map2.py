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


class MapGenerator2:

    def __init__(self, map_root):
        self.map_root = map_root

    def __floodfill(self, start: tuple[int, int], grid: list[list[int]], width: int, height: int, visited: set[tuple[int, int]]):
        # alrady visited
        if start in visited:
            return

        # wall
        if grid[start[1]][start[0]] == 1:
            return

        # now we did visit it
        visited.add(start)

        # recurse
        if start[0] > 0:
            self.__floodfill((start[0] - 1, start[1]), grid, width, height, visited)

        if start[0] < width - 1:
            self.__floodfill((start[0] + 1, start[1]), grid, width, height, visited)

        if start[1] > 0:
            self.__floodfill((start[0], start[1] - 1), grid, width, height, visited)

        if start[1] < height - 1:
            self.__floodfill((start[0], start[1] + 1), grid, width, height, visited)

    def __test_connected(self, grid: list[list[int]], width: int, height: int) -> bool:
        num_filled_sofar = sum((sum(i) for i in grid))

        for x in range(width):
            for y in range(height):
                if grid[y][x] == 0:
                    visited = set()
                    self.__floodfill((x, y), grid, width, height, visited)

                    if len(visited) == (width * height) - num_filled_sofar:
                        return True
                    else:
                        return False

        return False


    def __test_three_neighbour(self, grid: list[list[int]], num_agents: int) -> bool:
        return self.__num_3neighbors(grid) >= num_agents

    def __fill_one(self, grid: list[list[int]], width: int, height: int, num_agents: int):
        had = set()
        while True:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            if (x, y) in had:
                continue

            grid[y][x] = 1

            #                                                                       + 1 because we just filled one more
            connected = self.__test_connected(grid, width, height)
            enough_three_neighbour = self.__test_three_neighbour(grid, num_agents)

            if connected and enough_three_neighbour:
                return
            else:
                grid[y][x] = 0
                had.add((x, y))

            assert len(had) != (width * height) - sum((sum(i) for i in grid)), "can't fill any more"

    def generate_map(self, width: int,
                     height: int,
                     num_agents: List[int],
                     obstacle_percentage: float,
                     min_goal_distance: float = 0.5,
                     max_goal_distance: float = 1

                     ) -> Problem:

        grid = [[0 for _ in range(width)] for _ in range(height)]

        total_squares = width * height
        num_filled = int(total_squares * obstacle_percentage)
        total_num_agents = sum(num_agents)

        for _ in range(num_filled):
            self.__fill_one(grid, width, height, total_num_agents)

        starts, goals = self.__generate_agent_positions(grid, width, height, num_agents, min_goal_distance, max_goal_distance)

        start_locations: List[MarkedLocation] = []
        goal_locations: List[MarkedLocation] = []

        i = 0
        for color, team_size in enumerate(num_agents):
            for _ in range(team_size):
                start_locations.append(MarkedLocation(color, starts[i].x, starts[i].y))
                goal_locations.append(MarkedLocation(color, goals[i].x, goals[i].y))
                i += 1

        return Problem(grid, width, height, start_locations, goal_locations)

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

    def generate_map_file(self, name, width: int,
                          height: int,
                          num_agents: List[int],
                          obstacle_percentage: float,
                          min_goal_distance: float,
                          max_goal_distance: float):
        problem = self.generate_map(width, height, num_agents, obstacle_percentage, min_goal_distance, max_goal_distance)
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
                            obstacle_percentage: float = 0.75,
                            min_goal_distance: float = 0.5,
                            max_goal_distance: float = 1
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
            actions.append((name, width, height, num_agents, obstacle_percentage, min_goal_distance, max_goal_distance))

        with Pool(processes) as p:
            p.starmap(self.generate_map_file, actions)

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



if __name__ == '__main__':
    if not os.path.exists("test"):
        os.mkdir("test")

    map_generator = MapGenerator2("test")
    map_generator.generate_even_batch(
        200,  # number of maps
        20, 20,  # size
        3,  # number of agents
        3,  # number of teams
        prefix="test",
        min_goal_distance=0,
        obstacle_percentage=0.3
    )