from __future__ import annotations

from typing import Optional, TypeVar, Generic

from src.ctnode import CTNode
from src.data.agent import Agent
from src.grid import Grid
from src.paths import StandardFullSolution, AgentSolution, FullSolution

A = TypeVar("A", bound=Agent)


class LowLevelSolver(Generic[A]):
    def __init__(self, grid: Grid[A]):
        self.grid = grid

    def solve_all_agents(self, node: CTNode) -> Optional[FullSolution]:
        sol = StandardFullSolution()
        for agent in self.grid.agents:
            agent_solution = self.solve_for_agent(agent, node)
            if agent_solution is None:
                return None

            sol[agent] = agent_solution

        return sol

    def solve_for_agent(self, agent: A,
                        node: CTNode) -> Optional[AgentSolution]:
        raise NotImplementedError("Override this one!")
