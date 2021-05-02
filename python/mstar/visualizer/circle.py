from __future__ import annotations
import math

from pyglet import gl

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from python.mstar.visualizer import Window
from python.mstar.visualizer.drawable import Drawable


class Circle(Drawable):
    def __init__(self, steps=30):
        self.steps = steps

    def draw(self, window: Window, width, height, x=0, y=0):
        assert width == height
        radius = width / 2

        gl.glBegin(gl.GL_TRIANGLE_FAN)
        gl.glVertex2f(x, y)
        for i in range(self.steps + 1):
            gl.glVertex2f(
                (x + (radius * math.cos(i * math.tau / self.steps))),
                (y + (radius * math.sin(i * math.tau / self.steps)))
            )
        gl.glEnd()
