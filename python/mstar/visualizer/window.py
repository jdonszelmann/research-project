# from __future__ import annotations
#
# import pyglet
# from pyglet import gl
# from pyglet.window import key
#
# from typing import TYPE_CHECKING
#
# from python.mstar.visualizer.clickable import ClickType
#
# if TYPE_CHECKING:
#     from python.mstar.visualizer.grid import Grid
#     from python.mstar.visualizer.controls import Controls
#
#
# class Window(pyglet.window.Window):
#     def __init__(self, grid: Grid, controls: Controls):
#         config = pyglet.gl.Config(double_buffer=True, sample_buffers=1, samples=8)
#         super().__init__(config=config, resizable=True, width=640, height=480, caption="M*MAPFM visualization")
#
#         self.grid = grid
#         self.controls = controls
#
#         pyglet.clock.schedule_interval(self.update, 1/15)
#
#     def update(self, dt):
#         self.grid.update(dt)
#
#     def on_draw(self):
#         gl.glLoadIdentity()
#
#         gl.glClearColor(0.88, 0.8, 0.61, 1.0)
#         gl.glClear(gl.GL_COLOR_BUFFER_BIT)
#
#         gl.glEnable(gl.GL_BLEND)
#         gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
#
#         gl.glEnable(gl.GL_LINE_SMOOTH)
#         gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
#
#         width = self.width
#
#         self.grid.draw(self, width, max(self.height - 50, 0), 0, self.height)
#         self.controls.draw(self, width, 50, 0, 0)
#
#         gl.glFlush()
#         self.flip()
#
#     def on_key_press(self, symbol, modifiers):
#         if symbol == key.ESCAPE:
#             self.close()
#             return
#
#     def on_mouse_press(self, x, y, button, modifiers):
#         self.controls.click(self, x, y, ClickType.DOWN)
#         self.grid.click(self, x, y, ClickType.DOWN)
#
#     def on_mouse_release(self, x, y, button, modifiers):
#         self.controls.click(self, x, y, ClickType.UP)
#         self.grid.click(self, x, y, ClickType.UP)
