from math import inf
from typing import Optional

from python.mstar.rewrite.agent import Agent

from python.mstar.rewrite.config import Config
from python.mstar.rewrite.state import State
from python.mstar.rewrite.path_cache import PathCache


class OptimalPath:
    def __init__(self,
                 cfg: Config,
                 path_cache: PathCache,
                 goal_state: Optional[State] = None,  # only when cfg.prematch
                 ):
        self.cfg = cfg
        self.goal_state = goal_state

        self.path_cache = path_cache

    def shortest_path_for_agent_inmatch(self, agent: Agent) -> Agent:
        smallest = inf

        for i in self.path_cache.paths_for_colour(agent.colour):
            c = i[agent.location].move_cost
            if c < smallest:
                smallest = c

        return smallest

    def shortest_path_for_agent_prematch(self, agent: Agent) -> Agent:
        v = self.path_cache.paths_for_agent(agent, self)
        return v[agent.location].move_cost

    def shortest_path_for_agent(self, agent: Agent) -> Agent:
        if self.cfg.inmatch:
            return self.shortest_path_for_agent_inmatch(agent)
        else:
            return self.shortest_path_for_agent_prematch(agent)

    def __find_best_move_internal(self, agent, distance_to_goal):
        neighbour_costs = []
        for neighbour in self.path_cache.grid.get_empty_moves(agent.location):
            cost = distance_to_goal[neighbour].move_cost
            neighbour_costs.append((cost, neighbour))

        # there's always one minimum. That's because waiting is always possible
        min_cost, min_cost_neighbour = min(neighbour_costs, key=lambda i: i[0])

        return min_cost, agent.with_new_position(min_cost_neighbour)

    def best_move_inmatch(self, agent: Agent) -> list[Agent]:
        # return [
        #     self.__find_best_move_internal(agent, distance_to_goal)[1]
        #     for distance_to_goal in self.path_cache.paths_for_colour(agent.colour)
        # ]


        cost, best_move = min(
            (
                self.__find_best_move_internal(agent, distance_to_goal)
                for distance_to_goal in self.path_cache.paths_for_colour(agent.colour)
            ),

            key=lambda i: i[0]
        )

        return [best_move]


    def best_move_prematch(self, agent: Agent) -> list[Agent]:
        distance_to_goal = self.path_cache.paths_for_agent(agent, self)
        cost, best_move = self.__find_best_move_internal(agent, distance_to_goal)
        return [best_move]

    def best_move(self, agent: Agent) -> list[Agent]:
        if self.cfg.inmatch:
            return self.best_move_inmatch(agent)
        else:
            return self.best_move_prematch(agent)



