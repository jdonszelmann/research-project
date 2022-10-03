from __future__ import annotations

from collections import defaultdict
from queue import Queue
from typing import Optional, Dict, Set

from src.astar.astar_agent import AstarAgent
from src.astar.astar_grid import AstarGrid
from src.astar_base import AstarBase, AstarNode
from src.ctnode import CTNode
from src.data.constraints import Constraint, VertexConstraint, EdgeConstraint
from src.data.vertex import Vertex
from src.low_level import LowLevelSolver
from src.paths import AgentSolution


class AstarLowLevelAgentSolver(AstarBase):
    def __init__(self, grid: AstarGrid, agent: AstarAgent,
                 constraints: Set[Constraint],
                 shortest_paths: Dict[AstarAgent, Dict[Vertex, int]]):
        super().__init__(grid, agent.start)
        self.agent = agent

        self.t_constraints: Dict[int, Set[Constraint]] = defaultdict(set)
        for c in constraints:
            self.t_constraints[c.t].add(c)

        self.v_constraints: Dict[Vertex, Set[Constraint]] = defaultdict(set)
        for c in constraints:
            if isinstance(c, VertexConstraint):
                self.v_constraints[c.v].add(c)

        self.shortest_paths = shortest_paths

    def is_goal_state(self, state: AstarNode) -> bool:
        return self.agent.goal == state.v \
               and not self.is_constrained_in_future(state.v, state.t)

    def is_constrained_in_future(self, v: Vertex, curr_t: int) -> bool:
        return any(map(lambda c: c.t >= curr_t, self.v_constraints[v]))

    def heuristic(self, v: Vertex) -> int:
        return self.shortest_paths[self.agent][v]

    def get_vertex_at(self, x: int, y: int, current_state: AstarNode) -> bool:
        v = self.grid.get_vertex(x, y)
        if v is None:
            return False

        time_constraints = self.t_constraints[current_state.t + 1]

        violates_constraint = any(
            map(lambda c: self.is_constrained(current_state, v, c),
                time_constraints))

        return not violates_constraint

    @staticmethod
    def is_constrained(state: AstarNode, next_vertex: Vertex,
                       c: Constraint) -> bool:
        if isinstance(c, VertexConstraint):
            return c.v == next_vertex
        elif isinstance(c, EdgeConstraint):
            return c.e[0] == state.v and c.e[1] == next_vertex


class AstarLowLevelSolver(LowLevelSolver[AstarAgent]):
    def __init__(self, grid: AstarGrid):
        super().__init__(grid)

        shortest_paths: Dict[AstarAgent, Dict[Vertex, int]] = defaultdict(dict)

        for agent in grid.agents:
            visited_vs: Set[Vertex] = set()

            unvisited_vs: Queue[Vertex] = Queue()
            unvisited_vs.put(agent.goal)

            shortest_paths[agent][agent.goal] = 0

            while not unvisited_vs.empty():
                curr_v = unvisited_vs.get()

                visited_vs.add(curr_v)

                for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                    next_v = grid.get_vertex(curr_v.x + dx, curr_v.y + dy)
                    if next_v is not None and next_v not in visited_vs:
                        shortest_paths[agent][next_v] = shortest_paths[agent][curr_v] + 1  # yapf: disable
                        unvisited_vs.put(next_v)

        self.shortest_paths = shortest_paths

    def solve_for_agent(self, agent: AstarAgent,
                        node: CTNode) -> Optional[AgentSolution]:
        assert isinstance(self.grid, AstarGrid)

        agent_constraints = set(
            filter(lambda constr: constr.a_i == agent, node.constraints))
        agent_solver = AstarLowLevelAgentSolver(self.grid, agent,
                                                agent_constraints,
                                                self.shortest_paths)
        return agent_solver.solve()
