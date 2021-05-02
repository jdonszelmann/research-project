from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Protocol
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from python.mstar.visualizer import Window


class ClickType(Enum):
    DOWN = 0
    UP = 1


class Clickable(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def click(self, window: Window, x: float, y: float, click_type: ClickType): ...
