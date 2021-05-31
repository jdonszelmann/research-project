from python.coord import Coord
from python.mstar.rewrite.optimal_path import OptimalPath
from python.mstar.rewrite.state import State
from python.mstar.rewrite.config import Config
from python.mstar.rewrite.agent import Agent


class Heuristic:
    def __init__(self, cfg: Config, optimal_path: OptimalPath):
        self.cfg = cfg
        self.optimal_path = optimal_path

    def precalculated_heuristic(self, state: State) -> int:
        total_cost = 0
        for partial, actual in zip(state.identifier.partial, state.identifier.actual):
            if partial.is_uncalculated():
                total_cost += self.optimal_path.shortest_path_for_agent(actual)
            else:
                total_cost += self.optimal_path.shortest_path_for_agent(partial)

        return total_cost


    def manhattan_distance_to_goal_inmatch(self, agent: Agent) -> int:
        return min(
            Coord.from_marked_location(i).manhattan_distance(agent.location)
            for i in self.optimal_path.path_cache.goals
            if i.color == agent.colour
        )

    def manhattan_distance_to_goal_prematch(self, agent: Agent) -> int:
        gs = self.optimal_path.goal_state

        return gs.identifier.actual[agent.index].location.\
            manhattan_distance(agent.location)

    def manhattan_distance_to_goal(self, agent: Agent) -> int:
        if self.cfg.inmatch:
            return self.manhattan_distance_to_goal_inmatch(agent)
        else:
            return self.manhattan_distance_to_goal_prematch(agent)

    def distance_heuristic(self, state: State) -> int:
        total_cost = 0
        for partial, actual in zip(state.identifier.partial, state.identifier.partial):
            if partial.is_uncalculated():
                total_cost += self.manhattan_distance_to_goal(actual)
            else:
                total_cost += self.manhattan_distance_to_goal(partial)

        return total_cost

    def heuristic(self, state: State) -> int:
        if self.cfg.precompute_heuristic:
            return self.precalculated_heuristic(state)
        else:
            return self.distance_heuristic(state)
