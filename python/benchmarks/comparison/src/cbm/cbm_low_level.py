from typing import Optional, Set, Union

import logging

from src.cbm.cbm_agent import CBMTeam, CBMSingleAgentAstar
from src.cbm.cbm_grid import CBMGrid
from src.cbm.cbm_paths import CBMMakespanFullSolution, CBMAgentSolution, CBMSICFullSolution
from src.ctnode import CTNode
from src.data.constraints import Constraint
from src.low_level import LowLevelSolver
from src.paths import FullSolution, AgentSolution


class CBMLowLevelAgentSolver:
    def solve(self, t: int, find_makespan: bool) -> Optional[CBMAgentSolution]:
        raise NotImplementedError("Override this one")


class CBMLowLevelSolver(LowLevelSolver[CBMTeam]):
    T_max = 100

    def __init__(self, grid: CBMGrid, reset_teg: bool,
                 disappearing_agents: bool):
        super().__init__(grid)
        self.reset_teg = reset_teg
        self.disappearing_agents = disappearing_agents
        self.team_longest_path, self.sic_lb = CBMSingleAgentAstar.find_team_longest_path(
            grid)

        self.delta: Optional[int] = None

    def get_agent_solver(
            self, node: CTNode, team: CBMTeam,
            team_constraints: Set[Constraint]) -> CBMLowLevelAgentSolver:
        raise NotImplementedError("Override this one")

    def solve_all_agents(self, node: CTNode) -> Optional[FullSolution]:
        assert isinstance(self.grid, CBMGrid)

        sol = CBMMakespanFullSolution() if self.delta is None else CBMSICFullSolution()  # yapf: disable
        sol.disappearing_agents = self.disappearing_agents
        for team in self.grid.agents:
            team_solution = self.solve_for_agent(team, node)
            if team_solution is None:
                return None

            sol[team] = team_solution

        return sol

    def solve_for_agent(self, team: CBMTeam,
                        node: CTNode) -> Optional[AgentSolution]:
        assert isinstance(self.grid, CBMGrid)

        team_constraints = set(
            filter(lambda constr: constr.a_i == team, node.constraints))
        agent_solver = self.get_agent_solver(node, team, team_constraints)

        if node.cost is None:
            node.cost = self.team_longest_path[team]

        if self.delta is None:
            for T in range(node.cost, node.cost + self.T_max):
                solution = agent_solver.solve(T, True)
                if solution is not None:
                    logging.info(
                        f"Found makespan solution for lengths {list(map(lambda p: len(p[1]), solution))}, t{T}, team {team.id}"
                    )
                    return solution
        else:
            t = self.team_longest_path[team] + self.delta
            solution = agent_solver.solve(t, False)
            if solution is not None:
                logging.info(
                    f"Found SIC solution for lengths {list(map(lambda p: len(p[1]), solution))}, t{t}, team {team.id}"
                )
                return solution

        return None
