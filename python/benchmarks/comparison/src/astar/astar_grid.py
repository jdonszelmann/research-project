from typing import List

from mapfmclient import Problem, MarkedLocation

from src.astar.astar_agent import AstarAgent
from src.data.vertex import Vertex
from src.grid import Grid


class AstarGrid(Grid[AstarAgent]):
    def create_agents(self, problem: Problem) -> List[AstarAgent]:
        def find_first_goal(color: int,
                            locations: List[MarkedLocation]) -> Vertex:
            return next(
                self.get_vertex(g.x, g.y) for g in locations
                if g.color == color)

        return [
            AstarAgent(str(i), self.get_vertex(s.x, s.y),
                       find_first_goal(s.color, problem.goals))
            for i, s in enumerate(problem.starts)
        ]
