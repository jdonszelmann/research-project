from __future__ import annotations

from collections import defaultdict, deque

from mapfmclient import MarkedLocation

from python.coord import Coord
from python.mstar.bfsnode import BFSNode
from python.mstar.rewrite.agent import Agent
from python.mstar.rewrite.config import Config
from python.mstar.rewrite.grid import Grid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from python.mstar.rewrite import OptimalPath

PerColourTable = dict[
    int,  # colour
    list[
        dict[
            Coord,
            BFSNode
        ]
    ]
]

PerGoalTable = dict[
    Coord,  # goal location
    dict[
        Coord,
        BFSNode
    ]
]


def BFS(goal: Coord, grid: Grid):
    visited = {}
    q = deque()
    start_node = BFSNode(goal, 0, None)
    q.append(start_node)

    while len(q) != 0:
        curr = q.popleft()
        if curr.pos not in visited:
            visited[curr.pos] = curr
            for n in grid.get_empty_neighbours(curr.pos):
                if n not in visited:
                    q.append(BFSNode(n, curr.move_cost + 1, curr.pos))
    return visited


class PathCache:
    def __init__(self,
                 cfg: Config,
                 grid: Grid,
                 goals: list[MarkedLocation],
                 ):
        self.cfg = cfg
        self.grid = grid
        self.goals = goals

        self.per_colour: PerColourTable = defaultdict(list)
        self.per_goal: PerGoalTable = {}
        for index, goal in enumerate(self.goals):
            res = BFS(Coord(goal.x, goal.y), self.grid)

            self.per_colour[goal.color].append(res)
            self.per_goal[Coord(goal.x, goal.y)] = res

    def paths_for_colour(self, color: int) -> list[dict[Coord, BFSNode]]:
        return self.per_colour[color]

    def paths_for_agent(self, agent: Agent, optimal_path: OptimalPath) -> dict[Coord, BFSNode]:
        """
        Only use with prematch!
        """
        goal_location = optimal_path.goal_state.identifier.actual[agent.index]
        return self.per_goal[goal_location]
