from __future__ import annotations

from ctypes import Union

from mapfmclient import MarkedLocation


class Coord:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __hash__(self) -> int:
        return tuple.__hash__((self.x, self.y))

    def __eq__(self, other: Coord):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f"Coord({self.x}, {self.y})"

    def __iter__(self):
        yield self.x
        yield self.y

    def any_negative(self) -> bool:
        return self.x < 0 or self.y < 0

    def out_of_bounds(self, width, height) -> bool:
        return self.any_negative() or self.x >= width or self.y >= height

    def __sub__(self, other: Coord) -> Coord:
        return Coord(self.x - other.x, self.y - other.y)

    def __add__(self, other: Coord) -> Coord:
        return Coord(self.x + other.x, self.y + other.y)

    def __mul__(self, other: Union[Coord, int]) -> Coord:
        if isinstance(other, int):
            return Coord(self.x * other, self.y * other)
        else:
            return Coord(self.x * other.x, self.y * other.y)

    def manhattan_distance(self, other: Coord) -> int:
        diff = other.__sub__(self)
        return abs(diff.x) + abs(diff.y)

    @classmethod
    def from_marked_location(cls, m: MarkedLocation) -> Coord:
        return cls(m.x, m.y)


UncalculatedCoord = Coord(-1, -1)
