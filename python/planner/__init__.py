from abc import ABCMeta, abstractmethod
from typing import List

from python.planner.problem import Problem, State


class Planner(metaclass=ABCMeta):

    @abstractmethod
    def search(self, problem: Problem) -> List[State]: ...
