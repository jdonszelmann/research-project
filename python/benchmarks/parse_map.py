import os.path
from typing import Tuple, List

from mapfmclient import MarkedLocation, Problem


class MapParser:
    def __init__(self, map_root):
        self.map_root = map_root

    def parse_map(self, location: str):
        if location.endswith(".map"):
            path = os.path.join(self.map_root, location)
        else:
            path = os.path.join(self.map_root, location + ".map")
        with open(path) as f:
            lines = f.readlines()
        width_line = list(lines[0].split(" "))
        height_line = list(lines[1].split(" "))
        width = int(width_line[1])
        height = int(height_line[1])
        grid = []
        for i in range(height):
            grid.append([int(c == "@") for c in lines[2 + i] if c != "\n"])
        agents = int(lines[2 + height])
        starts = []
        starting_line = 3 + height

        for i in range(agents):
            start_line = list(lines[starting_line + i].split(" "))
            x = int(start_line[0])
            y = int(start_line[1])
            color = int(start_line[2])
            starts.append(MarkedLocation(color, x, y))

        goals = []
        starting_line = 4 + height + agents

        for i in range(agents):
            start_line = list(lines[starting_line + i].split(" "))
            x = int(start_line[0])
            y = int(start_line[1])
            color = int(start_line[2])
            goals.append(MarkedLocation(color, x, y))
        return Problem(grid, width, height, starts, goals)

    def parse_batch(self, folder) -> List[Tuple[str, Problem]]:
        paths = os.listdir(os.path.join(self.map_root, folder))
        return [(str(path), self.parse_map(str(os.path.join(folder, path)))) for path in paths]


