from __future__ import annotations

from abc import ABCMeta, abstractmethod

from mapfmclient import MarkedLocation

from python.mstar.rewrite import find_path
from python.mstar.rewrite.agent import Agent


class Goal(metaclass=ABCMeta):
    @abstractmethod
    def is_goal(self, state: find_path) -> bool: ...

    @abstractmethod
    def on_goal(self, agent: Agent) -> bool: ...


class StateGoal(Goal):
    def __init__(self, state: find_path):
        self.final_state = state

    def is_goal(self, state: find_path) -> bool:
        return state.identifier.actual == self.final_state.identifier.actual

    def on_goal(self, agent: Agent) -> bool:
        return self.final_state.identifier.actual[agent.index].location == agent.location


class AllAgentGoal(Goal):
    def __init__(self, goal_locations: list[MarkedLocation]):
        self.goal_locations = goal_locations


    def on_goal(self, agent: Agent) -> bool:
        for i in self.goal_locations:
            if i.x == agent.x and i.y == agent.y and i.color == agent.colour:
                return True

        return False

    def is_goal(self, state: find_path) -> bool:
        for agent in state.identifier.actual:
            if not self.on_goal(agent):
                return False

        return True

