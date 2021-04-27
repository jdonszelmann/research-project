from abc import abstractmethod
from collections import Iterable
from typing import Tuple

from python.planner import Problem, State


class AStarProblem(Problem):
    @abstractmethod
    def neighbours(self, parent: State) -> Iterable[Tuple[State, int]]:
        """

        :param parent:
        :return: a list of tuples containing the next state,
                 and the cost of going to that state.
        """
        raise NotImplemented
