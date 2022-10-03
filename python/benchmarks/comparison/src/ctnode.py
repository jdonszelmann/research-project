from __future__ import annotations

from typing import Set, Optional

from src.data.agent import Agent
from src.data.constraints import Constraint
from src.paths import FullSolution, AgentSolution
from src.debug.constraint_tree import ConstraintTree


class CTNode:
    def __init__(self, constraints: Set[Constraint],
                 ct: ConstraintTree) -> None:
        self.cost: Optional[int] = None
        self.constraints = constraints
        self.full_solution: Optional[FullSolution] = None
        self.ct = ct

    def add_constraint(self, constraint: Constraint) -> None:
        assert constraint not in self.constraints
        self.constraints = {*self.constraints, constraint}
        self.ct = self.ct.add_constraint(constraint)

    def update_sol(self, full_solution: FullSolution) -> None:
        self.full_solution = full_solution
        self.update_costs()

    def update_agent_path(self, agent: Agent,
                          agent_solution: AgentSolution) -> None:
        self.full_solution.update_agent(agent, agent_solution)
        self.update_costs()

    def update_costs(self) -> None:
        self.cost = self.full_solution.get_cost()

    def __lt__(self, other: CTNode) -> bool:
        return self.cost < other.cost
