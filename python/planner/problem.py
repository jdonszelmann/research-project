from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import Hashable, Tuple, Iterable, Callable

from python.priority_queue.unique_identifier import UniqueIdentifier


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


