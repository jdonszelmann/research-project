from __future__ import annotations

from python.coord import Coord


class BFSNode:
    def __init__(self, pos: Coord, move_cost, prev_pos):
        self.pos = pos
        self.move_cost = move_cost
        self.prev_pos = prev_pos

    def __gt__(self, other: BFSNode) -> bool:
        return self.move_cost > other.move_cost

    def __ge__(self, other: BFSNode) -> bool:
        return self.move_cost >= other.move_cost

    def __lt__(self, other: BFSNode) -> bool:
        return self.move_cost < other.move_cost

    def __le__(self, other: BFSNode) -> bool:
        return self.move_cost <= other.move_cost

    def __eq__(self, other: BFSNode) -> bool:
        return self.move_cost == other.move_cost
