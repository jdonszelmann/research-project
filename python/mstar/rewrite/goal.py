from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Iterable

from mapfmclient import MarkedLocation

from python.mstar.identifier import Identifier
from python.mstar.rewrite.state import State
from python.mstar.rewrite.agent import Agent


class Goal(metaclass=ABCMeta):
    @abstractmethod
    def is_goal(self, state: State) -> bool: ...

    @abstractmethod
    def on_goal(self, agent: Agent) -> bool: ...

    @abstractmethod
    def for_agents(self, agents: Iterable[Agent]) -> Goal: ...


class StateGoal(Goal):
    def __init__(self, state: State):
        self.final_state = state

    def is_goal(self, state: State) -> bool:
        return state.identifier.actual == self.final_state.identifier.actual

    def on_goal(self, agent: Agent) -> bool:

        # TODO: O(1) with dict
        for t_agent in self.final_state.identifier.actual:
            if t_agent.index == agent.index:
                return agent.location == t_agent.location

        else:
            assert False, f"no agent with index {agent.index}"

    def for_agents(self, agents: Iterable[Agent]) -> StateGoal:
        agents = frozenset(agent.index for agent in agents)

        ident_part = tuple(agent for agent in self.final_state.identifier.actual if agent.index in agents)

        return self.__class__(
            State(
                None,
                Identifier(
                    ident_part, ident_part
                ),
                self.final_state.collision_set.__class__(),
            )
        )


class AllAgentGoal(Goal):
    def __init__(self, goal_locations: list[MarkedLocation]):
        self.goal_locations = goal_locations


    def on_goal(self, agent: Agent) -> bool:
        for i in self.goal_locations:
            if i.x == agent.x and i.y == agent.y and i.color == agent.colour:
                return True

        return False

    def is_goal(self, state: State) -> bool:
        for agent in state.identifier.actual:
            if not self.on_goal(agent):
                return False

        return True

    def for_agents(self, agents: Iterable[Agent]) -> StateGoal:
        """
        atm not necessary as recursive mstar only works for prematching
        """
        raise NotImplemented

