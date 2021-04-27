from abc import abstractmethod, ABCMeta
from typing import TypeVar, Protocol, Generic

from python.priority_queue.comparable import Comparable
from python.priority_queue.unique_identifier import UniqueIdentifier


T = TypeVar('T', bound=Comparable)


class PriorityQueue(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def __contains__(self, item: T) -> bool:
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
