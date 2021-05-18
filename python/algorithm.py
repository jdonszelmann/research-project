from abc import ABC, abstractmethod

from mapfmclient import Problem, Solution


class MapfAlgorithm(ABC):
    @abstractmethod
    def solve(self, problem: Problem) -> Solution:
        raise NotImplemented

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplemented

    @property
    def version(self) -> str:
        return "0.0.1"
