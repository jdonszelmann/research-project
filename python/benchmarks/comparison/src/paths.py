from functools import reduce
from typing import List, Dict, Optional

from mapfmclient import Solution, Problem

from src.data.agent import Agent
from src.data.conflicts import Conflict
from src.data.vertex import Vertex
from src.grid import Grid
from src.util import get_first_conflict, to_mapf_tuples


class AgentSolution:
    """
    A solution for a single agent.
    This has no predefined methods and should work together with a corresponding FullSolution
    """
    pass


class StandardAgentSolution(List[Vertex], AgentSolution):
    pass


class FullSolution:
    def __init__(self):
        self.amount_of_conflicts: Optional[int] = None

    def get_cost(self) -> int:
        raise NotImplementedError("Override this one")

    def update_agent(self, agent: Agent, solution: AgentSolution) -> None:
        raise NotImplementedError("Override this one")

    def get_first_conflict(self) -> Optional[Conflict]:
        raise NotImplementedError("Override this one")

    def to_mapfm_solution(self, grid: Grid, problem: Problem) -> Solution:
        raise NotImplementedError("Override this one")


class StandardFullSolution(Dict[Agent, StandardAgentSolution], FullSolution):
    def get_cost(self) -> int:
        return reduce(lambda a, path: a + len(path), self.values(), 0)

    def update_agent(self, agent: Agent,
                     solution: StandardAgentSolution) -> None:
        self[agent] = solution

    def get_first_conflict(self) -> Optional[Conflict]:
        return get_first_conflict(self.items())

    def to_mapfm_solution(self, grid: Grid, problem: Problem) -> Solution:
        paths = [to_mapf_tuples(p) for p in self.values()]
        return Solution.from_paths(paths)
