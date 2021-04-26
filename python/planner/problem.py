from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import Hashable, Tuple, Iterable, Callable

from python.queue.unique_identifier import UniqueIdentifier


class State(Hashable, UniqueIdentifier, metaclass=ABCMeta):
    @abstractmethod
    def __eq__(self, other: State):
        raise NotImplemented


class Problem(metaclass=ABCMeta):
    @abstractmethod
    def initial_state(self) -> State:
        raise NotImplemented

    @abstractmethod
    def final_state(self, state: State) -> bool:
        raise NotImplemented

    @abstractmethod
    def heuristic(self, state: State) -> int:
        raise NotImplemented


class AStarProblem(Problem):
    @abstractmethod
    def neighbours(self, parent: State) -> Iterable[Tuple[State, int]]:
        """

        :param parent:
        :return: a list of tuples containing the next state,
                 and the cost of going to that state.
        """
        raise NotImplemented


class MStarProblem(Problem):
    @abstractmethod
    def neighbours(self, parent: State) -> Iterable[Tuple[State, int]]:
        """

        :param parent: parent state
        :param in_queue: a function returning if a certain state is in the queue
        :return: a list of tuples containing the next state,
                 and the cost of going to that state.
        """
        raise NotImplemented
