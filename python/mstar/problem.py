from abc import ABC, abstractmethod
from collections import Iterable, Callable

from python.mstar.state import MStarState
from python.planner import Problem


class MStarProblem(Problem, ABC):
    @abstractmethod
    def neighbours(self, parent: MStarState, in_queue: Callable[[MStarState], bool]) -> Iterable[MStarState]: ...
