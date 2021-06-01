from __future__ import annotations

# import threading
# import time
from collections import Callable

# import pyglet.app

# from python.mstar.visualizer.controls import Controls
# from python.mstar.visualizer.grid import Grid
# from python.mstar.visualizer.window import Window
# from threading import Thread

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from python.mstar.mstar import State


class Visualizer:
    def __init__(self, *args, **kwargs):
        pass
        # self.grid = Grid(
        #     *args,
        #     **kwargs,
        # )
        # self.controls = Controls(self.grid)
        # self.window = Window(self.grid, self.controls)

    def submit_state(self, state: State):
        pass
        # self.grid.submit_state(state)

    @staticmethod
    def run(func: Callable, *args, **kwargs):
        pass
        # t = Thread(target=func, args=args, kwargs=kwargs)
        # t.daemon = False
        # t.start()
        #
        # pyglet.app.run()

    def end_sim(self):
        pass
        # self.grid.end_sim()
