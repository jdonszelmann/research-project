from abc import abstractmethod, ABCMeta
from typing import TypeVar, Protocol

from python.queue.comparable import Comparable
from python.queue.unique_identifier import UniqueIdentifier


class ComparableAndUniquelyIdentifiable(Comparable, UniqueIdentifier, Protocol):
    pass


T = TypeVar('T', bound=ComparableAndUniquelyIdentifiable)


class PriorityQueue(metaclass=ABCMeta):
    @abstractmethod
    def __contains__(self, item: UniqueIdentifier) -> bool:
        raise NotImplemented

    @abstractmethod
    def enqueue(self, item: T):
        raise NotImplemented

    @abstractmethod
    def dequeue(self) -> T:
        raise NotImplemented

    @abstractmethod
    def empty(self) -> bool:
        raise NotImplemented
