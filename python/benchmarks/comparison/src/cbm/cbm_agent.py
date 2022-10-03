from __future__ import annotations

from collections import defaultdict
from typing import List, Dict

from src.astar_base import AstarBase, AstarNode
from src.data.agent import Agent
from src.data.vertex import Vertex
from src.grid import Grid


class CBMAgent(Agent):
    def __init__(self, id: int, team: CBMTeam, start: Vertex):
        super().__init__(f"A{id}T{team.id}")
        self.start = start
        self.team = team


class CBMTeam(Agent):
    def __init__(self, team_id: int, agents: List[CBMAgent],
                 goals: List[Vertex]):
        super().__init__(f"T{team_id}")
        self.agents = agents
        self.goals = goals


class CBMSingleAgentAstar(AstarBase):
    def __init__(self, grid: Grid, agent: CBMAgent, team: CBMTeam):
        super().__init__(grid, agent.start, False)
        self.team = team

    def heuristic(self, v: Vertex) -> int:
        return min(
            map(lambda g: abs(v.x - g.x) + abs(v.y - g.y), self.team.goals))

    def is_goal_state(self, state: AstarNode) -> bool:
        return state.v in self.team.goals

    @staticmethod
    def find_team_longest_path(grid: Grid) -> (Dict[CBMTeam, int], int):
        team_longest_path: Dict[CBMTeam, int] = defaultdict(lambda: 0)
        sic_lb = 0
        for team in grid.agents:
            for agent in team.agents:
                agent_sol = CBMSingleAgentAstar(grid, agent, team).solve()
                assert agent_sol is not None
                sic_lb += len(agent_sol)
                team_longest_path[team] = max(team_longest_path[team],
                                              len(agent_sol))

        return team_longest_path, sic_lb
