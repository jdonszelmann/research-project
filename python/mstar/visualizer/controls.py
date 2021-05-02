from __future__ import annotations

from collections import Callable

import pyglet
from pyglet import gl

from python.mstar.visualizer.clickable import Clickable, ClickType
from python.mstar.visualizer.drawable import Drawable

from typing import TYPE_CHECKING

from python.mstar.visualizer.sprites import Next, Prev, End, Stop, Parent, Child, NextChild

if TYPE_CHECKING:
    from python.mstar.visualizer import Window, Grid

button_color = (1, 1, 1, 1)
button_color_pressed = (0.8, 0.8, 0.8, 1)
bg_color = (0, 0, 0, 1)


class Button(Drawable, Clickable):
    def __init__(self, grid: Grid, on_click: Callable, sprite: Drawable):
        self.grid = grid
        self.on_click = on_click
        self.x = None
        self.y = None
        self.width = None
        self.height = None

        self.sprite = sprite

        self.clicked = False

    def draw(self, window: Window, width, height, x=0, y=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if self.clicked:
            gl.glColor4f(*button_color_pressed)
        else:
            gl.glColor4f(*button_color)
        self.sprite.draw(window, width, height, x, y)

    def click(self, window: Window, x: float, y: float, click_type: ClickType):
        if self.x < x < self.x + self.width and self.y > y > self.y - self.height:
            if click_type == ClickType.DOWN:
                self.clicked = True
            else:
                self.on_click()
                self.clicked = False
        else:
            self.clicked = False


class Controls(Drawable, Clickable):
    def __init__(self, grid: Grid):
        self.buttons = []
        self.grid = grid

        self.buttons.append(
            Button(
                self.grid,
                grid.next_child,
                NextChild(),
            )
        )

        self.buttons.append(
            Button(
                self.grid,
                grid.prev,
                Prev(),
            )
        )

        self.buttons.append(
            Button(
                self.grid,
                grid.parent,
                Parent(),
            )
        )

        self.buttons.append(
            Button(
                self.grid,
                grid.stop_search,
                Stop(),
            )
        )

        self.buttons.append(
            Button(
                self.grid,
                grid.child,
                Child(),
            )
        )

        self.buttons.append(
            Button(
                self.grid,
                grid.next,
                Next(),
            )
        )

        self.buttons.append(
            Button(
                self.grid,
                grid.end,
                End(),
            )
        )

    def draw(self, window: Window, width, height, x=0, y=0):
        pyglet.graphics.draw(
            4, gl.GL_QUADS,
            ('v2f', (
                x, y + height,
                x + width, y + height,
                x + width, y,
                x, y
            )),
            ('c4f', (*bg_color, *bg_color, *bg_color, *bg_color)),
        )

        length = min(width, height)

        middle = width / 2
        buttons_width = length * len(self.buttons)
        start_x = middle - (buttons_width / 2)

        curr_x = start_x
        for i in self.buttons:
            curr_x += length
            i.draw(window, length, length, curr_x, y + length)

    def click(self, window: Window, x: float, y: float, click_type: ClickType):
        for i in self.buttons:
            i.click(window, x, y, click_type)
