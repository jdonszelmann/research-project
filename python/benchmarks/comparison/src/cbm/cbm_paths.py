from __future__ import annotations

from collections import OrderedDict
from typing import Optional, List, Tuple

from mapfmclient import Solution, Problem

from src.data.conflicts import Conflict
from src.data.vertex import Vertex
from src.cbm.cbm_agent import CBMTeam, CBMAgent
from src.grid import Grid
from src.paths import FullSolution, AgentSolution
from src.util import get_first_conflict, to_mapf_tuples, flatten


class CBMAgentSolution(List[Tuple[CBMAgent, List[Vertex]]], AgentSolution):
    pass


class CBMFullSolution(OrderedDict[CBMTeam, CBMAgentSolution], FullSolution):
    def __init__(self):
        super().__init__()
        self.disappearing_agents = False

    def update_agent(self, agent: CBMTeam, solution: CBMAgentSolution) -> None:
        self[agent] = solution

    def get_first_conflict(self) -> Optional[Conflict]:
        def do_compare(a_i: CBMAgent, a_j: CBMAgent) -> bool:
            return a_i.team is not a_j.team

        def agent_disappears(v: Vertex, a: CBMAgent) -> bool:
            return self.disappearing_agents and v in a.team.goals

        conflict = get_first_conflict(self.get_sorted_flattened_paths(),
                                      do_compare=do_compare,
                                      agent_disappears=agent_disappears)
        if conflict is None:
            return None

        if conflict.t == 0:
            raise Exception("Conflict at t = 0, check the map!")

        assert isinstance(conflict.a_i, CBMAgent)
        assert isinstance(conflict.a_j, CBMAgent)

        conflict.a_i = conflict.a_i.team
        conflict.a_j = conflict.a_j.team

        return conflict

    def to_mapfm_solution(self, grid: Grid, problem: Problem) -> Solution:
        paths = self.get_sorted_flattened_paths()
        mapfm_paths: List[List[Tuple[int, int]]] = []

        for start in problem.starts:
            for path in paths:
                if path[0].start is grid.get_vertex(start.x, start.y):
                    mapfm_paths.append(to_mapf_tuples(path[1]))

        return Solution.from_paths(mapfm_paths)

    def get_sorted_flattened_paths(
            self) -> List[Tuple[CBMAgent, List[Vertex]]]:
        return sorted(self.get_flattened_paths(), key=lambda kv: kv[0].id)

    def get_flattened_paths(self) -> List[Tuple[CBMAgent, List[Vertex]]]:
        return flatten(self.values())

    def get_cost(self) -> int:
        raise NotImplementedError("Override this one")


class CBMMakespanFullSolution(CBMFullSolution):
    def get_cost(self) -> int:
        # We need a makespan, which we obtain with this -1 (since at T11, path length is 12)
        return max(map(lambda p: len(p[1]), self.get_flattened_paths())) - 1


class CBMSICFullSolution(CBMFullSolution):
    def get_cost(self) -> int:
        def get_actual_cost(path: List[Vertex]) -> int:
            minus_cost = 0

            last_v: Optional[Vertex] = None
            for v in reversed(path):
                if last_v is None:
                    last_v = v
                elif v is not last_v:
                    break
                else:
                    minus_cost += 1

            return len(path) - minus_cost

        return sum(
            map(lambda p: get_actual_cost(p[1]), self.get_flattened_paths()))
