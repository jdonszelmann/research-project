# from __future__ import annotations
#
# import time
# from enum import Enum
# from typing import List, Optional
#
# import pyglet
# from pyglet import gl
#
# from mapfmclient import MarkedLocation
#
# from typing import TYPE_CHECKING
#
# from python.mstar.visualizer.circle import Circle
# from python.mstar.visualizer.clickable import Clickable, ClickType
#
# if TYPE_CHECKING:
#     from python.mstar.mstar import State
#
# from python.mstar.visualizer.drawable import Drawable
# from python.mstar.visualizer.sprites import Goal, Start, Wall, Agent
# from python.mstar.visualizer.window import Window
#
# colors = [
#     (0.8, 0.27, 0.32, 1.0),
#     (0.14, 0.38, 0.5, 1.0),
#     (0.5, 0.11, 0.15, 1.0),
#     (0.18, 0.6, 0.8, 1.0),
#     (0.07, 0.5, 0.16, 1.0),
#     (0.26, 0.8, 0.38, 1.0),
#     (0.22, 0.8, 0.68, 1.0),
#     (0.4, 0.32, 0.29, 1.0),
#     (0.5, 0.49, 0.09, 1.0),
#     (0.8, 0.44, 0.31, 1.0)
# ]
# wall_color = (0.45, 0.19, 0.28, 1.0)
# bg_color = (0.88, 0.8, 0.61, 1.0)
# line_color = (0.1, 0.1, 0.1, 0.2)
# black = (0, 0, 0, 1)
# grid_outside_color = wall_color
#
# selected_agent_color = wall_color
# unselected_agent_color = (wall_color[0] * 0.5, wall_color[1] * 0.5, wall_color[2] * 0.5, 1.0)
#
#
# class SearchForType(Enum):
#     Parent = 0
#     Child = 1
#     Nothing = 3
#
#
# class Square:
#     def __init__(self,
#                  goal: Optional[int] = None,
#                  start: Optional[int] = None,
#                  wall: bool = False
#                  ):
#         self.goal = goal
#         self.start = start
#         self.wall = wall
#
#         self.length = None
#
#     def draw(self, window: Window, width, height, x=0, y=0):
#         if self.wall:
#             gl.glColor4f(*wall_color)
#             Wall().draw(window, width, height, x, y)
#         else:
#             if self.start is not None:
#                 gl.glColor4f(*colors[self.start])
#                 Start().draw(window, width, height, x, y + 5)
#
#             if self.goal is not None:
#                 gl.glColor4f(*colors[self.goal])
#                 Goal().draw(window, width, height, x, y)
#
#     def __repr__(self):
#         res = []
#         if self.wall:
#             res.append("wall")
#         else:
#             if self.goal:
#                 res.append("goal")
#
#             if self.start:
#                 res.append("start")
#
#         return " ".join(res) if res else "empty"
#
#
# class AgentOverview(Drawable, Clickable):
#     def __init__(self, grid: Grid, color: int):
#         self.color = color
#         self.selected = False
#         self.grid = grid
#
#         self.x = None
#         self.y = None
#         self.width = None
#         self.height = None
#
#     def draw(self, window: Window, width, height, x=0, y=0):
#         self.x = x
#         self.y = y
#         self.width = width
#         self.height = height
#
#         if self.selected:
#             color = selected_agent_color
#         else:
#             color = unselected_agent_color
#
#         pyglet.graphics.draw(
#             4, gl.GL_QUADS,
#             ('v2f', (
#                 x, y,
#                 x + self.width, y,
#                 x + self.width, y - self.height,
#                 x, y - self.height
#             )),
#             ('c4f', (*black, *black, *black, *black)),
#         )
#         border = 1
#         pyglet.graphics.draw(
#             4, gl.GL_QUADS,
#             ('v2f', (
#                 x + border, y - border,
#                 x - border + self.width, y - border,
#                 x - border + self.width, y + border - self.height,
#                 x + border, y + border - self.height
#             )),
#             ('c4f', (*color, *color, *color, *color)),
#         )
#
#         gl.glColor4f(*map(
#             lambda i: i * 1.1
#             if self.selected
#             else i * 0.5, colors[self.color][:3]
#         ), colors[self.color][3])
#         Agent().draw(window, self.height, self.height, x + border, y - border)
#
#     def click(self, window: Window, x: float, y: float, click_type: ClickType):
#         if self.x < x < self.x + self.width and self.y > y > self.y - self.height:
#             if click_type == ClickType.DOWN:
#                 for i in self.grid.agent_overviews:
#                     i.selected = False
#                 self.selected = True
#
#
# class Grid(Drawable, Clickable):
#     def __init__(self,
#                  walls: List[List[int]],
#                  starts: List[MarkedLocation],
#                  ends: List[MarkedLocation],
#                  width,
#                  height,
#                  ):
#         self.walls = walls
#         self.starts = starts
#         self.ends = ends
#
#         self.width = width
#         self.height = height
#
#         self.grid: List[List[Square]] = []
#
#         for y in range(height):
#             row = []
#             for x in range(width):
#                 goal = next((i.color for i in self.ends if i.x == x and i.y == y), None)
#                 start = next((i.color for i in self.starts if i.x == x and i.y == y), None)
#                 row.append(Square(
#                     wall=self.walls[y][x] == 1,
#                     goal=goal,
#                     start=start,
#                 ))
#
#             self.grid.append(row)
#
#         self.states: List[State] = []
#         self.current_timestep: int = 0
#
#         self.search_for: Optional[State] = None
#         self.search_for_type: SearchForType = SearchForType.Nothing
#
#         self.waiting: bool = False
#         self.ended = False
#
#         self.agent_overviews: List[AgentOverview] = []
#
#     def submit_state(self, state: State):
#         print("new state")
#         self.states.append(state)
#
#         print(f"{self.current_timestep} / {len(self.states)}")
#
#         if self.current_timestep < len(self.states) and not self.ended:
#             print("waiting")
#             self.waiting = True
#             while self.current_timestep < len(self.states) and not self.ended:
#                 time.sleep(0.1)
#             print("continuing")
#             self.waiting = False
#
#     def current_state(self) -> Optional[State]:
#         if 0 <= self.current_timestep < len(self.states):
#             return self.states[self.current_timestep]
#         elif len(self.states) > 0:
#             return self.states[-1]
#         else:
#             return None
#
#     def click(self, window: Window, x: float, y: float, click_type: ClickType):
#         for i in self.agent_overviews:
#             i.click(window, x, y, click_type)
#
#     def draw(self, window: Window, width, height, x=0, y=0):
#         actual_width = self.draw_grid(window, width * (2 / 3), height, x, y)
#         self.draw_agent_overview(window, width - actual_width, height, x + actual_width, y)
#
#     def draw_agent_overview(self, window: Window, width, height, x=0, y=0):
#         curr_y = y
#
#         if (curr_state := self.current_state()) is not None:
#             height_per_agent = height / len(curr_state.identifier.actual)
#
#             for index, i in enumerate(curr_state.identifier.actual):
#                 if index >= len(self.agent_overviews):
#                     self.agent_overviews.append(AgentOverview(
#                         self,
#                         i.color,
#                     ))
#                 o = self.agent_overviews[index]
#                 o.draw(window, width, height_per_agent, x, curr_y)
#                 curr_y -= height_per_agent
#
#     def draw_grid(self, window: Window, width, height, x=0, y=0):
#         length = min(width, height) / max(self.width, self.height)
#
#         actual_width = length * self.width
#         actual_height = length * self.height
#
#         pyglet.graphics.draw(
#             4, gl.GL_QUADS,
#             ('v2f', (
#                 x, y,
#                 x + actual_width, y,
#                 x + actual_width, y - actual_height,
#                 x, y - actual_height
#             )),
#             ('c4f', (*bg_color, *bg_color, *bg_color, *bg_color)),
#         )
#
#         for s_y, row in enumerate(self.grid):
#             for s_x, s in enumerate(row):
#                 if s.wall:
#                     gl.glPushMatrix()
#                     s.draw(window, length, length, x + s_x * length, y - s_y * length)
#                     gl.glPopMatrix()
#
#         gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
#         gl.glLineWidth(2)
#         for ly in range(1, self.height):
#             pyglet.graphics.draw(
#                 2, gl.GL_LINES,
#                 ('v2f', (
#                     x, y - ly * length,
#                     x + actual_width, y - ly * length)),
#                 ('c4f', (*line_color, *line_color)),
#             )
#
#         for lx in range(1, self.width):
#             pyglet.graphics.draw(
#                 2, gl.GL_LINES,
#                 ('v2f', (
#                     lx * length, y,
#                     lx * length, y - actual_height)),
#                 ('c4f', (*line_color, *line_color)),
#             )
#         gl.glPopAttrib(gl.GL_ALL_ATTRIB_BITS)
#
#         for s_y, row in enumerate(self.grid):
#             for s_x, s in enumerate(row):
#                 if not s.wall:
#                     gl.glPushMatrix()
#                     s.draw(window, length, length, x + s_x * length, y - s_y * length)
#                     gl.glPopMatrix()
#
#         if (curr_state := self.current_state()) is not None:
#             path = curr_state.backtrack()
#             for index, i in enumerate(self.agent_overviews):
#                 if i.selected:
#                     if len(path) > 0:
#                         prev = path[0].identifier.actual[index]
#                         for s in path[1:]:
#                             loc = s.identifier.actual[index]
#
#                             color = (*colors[loc.color][:3], 0.5)
#
#                             gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
#                             gl.glLineWidth(4)
#                             pyglet.graphics.draw(
#                                 2, gl.GL_LINES,
#                                 ('v2f', (
#                                     x + loc.x * length + length / 2,
#                                     y - loc.y * length - length / 2,
#                                     x + prev.x * length + length / 2,
#                                     y - prev.y * length - length / 2,
#                                 )),
#                                 ('c4f', (*color, *color)),
#                             )
#                             gl.glPopAttrib(gl.GL_ALL_ATTRIB_BITS)
#
#                             prev = loc
#
#             if curr_state.is_standard:
#                 for index, c in enumerate(curr_state.identifier.actual):
#                     gl.glColor4f(*map(
#                         lambda i: i * 1.1
#                         if index < len(self.agent_overviews) and self.agent_overviews[index].selected
#                         else i * 0.5, colors[c.color][:3]
#                     ), colors[c.color][3])
#                     Agent().draw(window, length, length, x + c.x * length, y - c.y * length)
#             else:
#                 for index, c in enumerate(curr_state.identifier.actual):
#                     gl.glColor4f(0.3, 0.3, 0.3, 0.7)
#                     Agent().draw(window, length, length, x + c.x * length, y - c.y * length)
#
#
#                 for index, c in enumerate(curr_state.identifier.partial):
#                     gl.glColor4f(*map(
#                         lambda i: i * 1.1
#                         if index < len(self.agent_overviews) and self.agent_overviews[index].selected
#                         else i * 0.5, colors[c.color][:3]
#                     ), colors[c.color][3])
#                     Agent().draw(window, length, length, x + c.x * length, y - c.y * length)
#
#         return actual_width
#
#     def next(self):
#         self.current_timestep += 1
#         print(f"{self.current_timestep} / {len(self.states)}")
#
#     def prev(self):
#         if self.current_timestep > 0:
#             self.current_timestep -= 1
#         print(f"{self.current_timestep} / {len(self.states)}")
#
#     def child(self):
#         if 0 <= self.current_timestep < len(self.states):
#             curr_state = self.states[self.current_timestep]
#             self.search_for = curr_state
#             self.search_for_type = SearchForType.Child
#
#     def parent(self):
#         if (curr_state := self.current_state()) is not None:
#             self.search_for = curr_state
#             self.search_for_type = SearchForType.Parent
#
#     def end(self):
#         self.current_timestep = len(self.states)
#         print(f"{self.current_timestep} / {len(self.states)}")
#
#     def end_sim(self):
#         self.ended = True
#
#     def stop_search(self):
#         self.search_for_type = SearchForType.Nothing
#
#     def next_child(self):
#         if (curr_state := self.current_state()) is not None:
#             if curr_state.parent is not None:
#                 self.search_for = curr_state.parent
#                 self.search_for_type = SearchForType.Child
#
#     def update(self, _dt):
#         if self.waiting:
#             if self.search_for_type == SearchForType.Child:
#                 self.current_timestep += 1
#                 print(f"{self.current_timestep} / {len(self.states)}")
#
#                 if (curr_state := self.current_state()) is not None and curr_state.parent == self.search_for:
#                     self.search_for = None
#                     self.search_for_type = SearchForType.Nothing
#
#             elif self.search_for_type == SearchForType.Parent:
#                 if self.current_timestep > 0:
#                     self.current_timestep -= 1
#                     print(f"{self.current_timestep} / {len(self.states)}")
#
#                     if (curr_state := self.current_state()) is not None:
#                         self.search_for = None
#                         self.search_for_type = SearchForType.Nothing
#                     elif curr_state is None or curr_state == self.search_for.parent:
#                         self.search_for = None
#                         self.search_for_type = SearchForType.Nothing
