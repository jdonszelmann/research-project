from __future__ import annotations

from typing import Optional

from mapfmclient import MarkedLocation

from python.coord import Coord, UncalculatedCoord


class Agent:
    def __init__(
            self,
            location: Coord,
            colour: int,
            accumulated_cost: Optional[int],
            index: int,

            uncalculated=False,
    ):
        self.location = location
        self.accumulated_cost = accumulated_cost if accumulated_cost else 0
        self.colour = colour
        self.index: int = index

        self.uncalculated = uncalculated

    def make_uncalculated(self) -> Agent:
        return Agent(Coord(0, 0), self.colour, self.index, self.accumulated_cost, uncalculated=True)

    def is_uncalculated(self) -> bool:
        return self.uncalculated

    @property
    def x(self):
        return self.location.x

    @property
    def y(self):
        return self.location.y

    def __eq__(self, other: Agent):
        if other is self:
            return True
        return self.location == other and self.accumulated_cost == other.accumulated_cost

    def __hash__(self):
        return hash(self.location) ^ hash(self.accumulated_cost)

    def __repr__(self):
        if self.is_uncalculated():
            return "UncalculatedAgent"
        else:
            return f"Agent({self.location}, {self.accumulated_cost}, {self.index})"

    @classmethod
    def from_marked_location(cls, location: MarkedLocation, accumulated_cost: int, index: int) -> Agent:
        return cls(Coord(location.x, location.y), location.color, accumulated_cost, index)

    def with_new_position(self, new_pos: Coord) -> Agent:
        return Agent(new_pos, self.colour, self.accumulated_cost, self.index)

