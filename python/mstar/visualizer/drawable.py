from abc import abstractmethod, ABCMeta
from typing import Protocol

from python.mstar.visualizer.window import Window


class Drawable(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def draw(self, window: Window, width, height, x=0, y=0): ...
