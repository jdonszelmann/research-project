from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Hashable, Tuple, Iterable


class State(ABC, Hashable):
    @abstractmethod
    def __eq__(self, other: State):
        pass


class Problem(ABC):
    @abstractmethod
    def neighbours(self, parent: State) -> Iterable[Tuple[State, int]]:
        """

        :param parent:
        :return: a list of tuples containing the next state,
                 and the cost of going to that state.
        """
        raise NotImplemented

    @abstractmethod
    def initial_state(self) -> State:
        raise NotImplemented

    @abstractmethod
    def final_state(self, state: State) -> bool:
        raise NotImplemented

    @abstractmethod
    def heuristic(self, state: State) -> int:
        raise NotImplemented
