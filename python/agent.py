from __future__ import annotations

from mapfmclient import MarkedLocation

from python.coord import Coord


class Agent:
    def __init__(self, location: Coord, color: int, accumulated_cost: Optional[int]):
        self.location = location
        self.accumulated_cost = accumulated_cost if accumulated_cost else 0
        self.color = color

    @property
    def x(self):
        return self.location.x

    @property
    def y(self):
        return self.location.y

    def __eq__(self, other: Agent):
        return self.location == other and self.accumulated_cost == other.accumulated_cost

    def __hash__(self):
        return tuple.__hash__((self.location, self.accumulated_cost))

    def __repr__(self):
        return f"Agent({self.location}, acc_cost{self.accumulated_cost})"

    @classmethod
    def from_marked_location(cls, location: MarkedLocation, accumulated_cost: int) -> Agent:
        return cls(Coord(location.x, location.y), location.color, accumulated_cost)
