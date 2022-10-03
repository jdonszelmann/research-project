from typing import List

from mapfmclient import Problem

from src.cbm.cbm_agent import CBMAgent, CBMTeam
from src.grid import Grid


class CBMGrid(Grid[CBMTeam]):
    def create_agents(self, problem: Problem) -> List[CBMTeam]:
        colors = set(map(lambda ml: ml.color, problem.starts))

        teams = {color: CBMTeam(color, [], []) for color in colors}

        for i, s in enumerate(problem.starts):
            team = teams[s.color]
            team.agents.append(CBMAgent(i, team, self.get_vertex(s.x, s.y)))

        for i, g in enumerate(problem.goals):
            team = teams[g.color]
            team.goals.append(self.get_vertex(g.x, g.y))

        return list(teams.values())
