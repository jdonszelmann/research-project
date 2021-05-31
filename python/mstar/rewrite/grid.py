from typing import Optional, Iterable

from python.coord import Coord

directions = [Coord(0, -1), Coord(0, 1), Coord(1, 0), Coord(-1, 0)]


class Grid:
    def __init__(self, grid: list[list[int]],
                 width: Optional[int] = None,
                 height: Optional[int] = None
                 ):
        self.grid = grid
        self.height = len(grid)

        if self.height > 0:
            first = len(grid[0])
            for i in grid[1:]:
                assert len(i) == first

            self.width = first

        else:
            self.width = 0

        if width is not None:
            assert self.width == width
        if height is not None:
            assert self.height == height

    def wall_at(self, coord: Coord) -> bool:
        return self.grid[coord.y][coord.x] == 1

    def get_neighbours(self, position: Coord) -> Iterable[Coord]:
        """
        Lists all neighbour grid positions which are in bounds
        """

        for i in directions:
            n = i + position
            if not n.out_of_bounds(self.width, self.height):
                yield n

    def get_moves(self, position: Coord) -> Iterable[Coord]:
        """
        Lists all neighbour grid positions which are in bounds. Also return current
        position to allow for waiting
        """
        yield position
        yield from self.get_neighbours(position)

    def get_empty_neighbours(self, position: Coord) -> Iterable[Coord]:
        """
        Lists all neighbour grid positions which are in bounds and not walls
        """
        return filter(
            lambda i: not self.wall_at(i),
            self.get_neighbours(position)
        )

    def get_empty_moves(self, position: Coord) -> Iterable[Coord]:
        return filter(
            lambda i: not self.wall_at(i),
            self.get_moves(position)
        )
