import os
from contextlib import nullcontext
from pathlib import Path

import pyglet

from python.mstar.visualizer.drawable import Drawable
from python.mstar.visualizer.shaders import Shader
from python.mstar.visualizer.window import Window
from pyglet import image
from pyglet import gl

path = Path(os.path.dirname(os.path.realpath(__file__)))

goal_sprite = image.load(path / "assets" / "goal.png")
start_sprite = image.load(path / "assets" / "start.png")
agent_sprite = image.load(path / "assets" / "agent.png")
wall_sprite = image.load(path / "assets" / "wall.png")

next_sprite = image.load(path / "assets" / "next.png")
prev_sprite = image.load(path / "assets" / "prev.png")
parent_sprite = image.load(path / "assets" / "out.png")
child_sprite = image.load(path / "assets" / "in.png")
stop_sprite = image.load(path / "assets" / "stop.png")
next_child_sprite = image.load(path / "assets" / "next_child.png")
end_sprite = image.load(path / "assets" / "end.png")


sprite_shader = Shader([path / "assets" / "sprite_shader.vert"], [path / "assets" / "sprite_shader.frag"])
button_shader = Shader([path / "assets" / "button_shader.vert"], [path / "assets" / "button_shader.frag"])


class Goal(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, goal_sprite)


class Start(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, start_sprite)


class Agent(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, agent_sprite)


class Wall(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, wall_sprite)


class Next(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, next_sprite, button_shader)


class Prev(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, prev_sprite, button_shader)


class Parent(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, parent_sprite, button_shader)


class Child(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, child_sprite, button_shader)


class Stop(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, stop_sprite, button_shader)


class NextChild(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, next_child_sprite, button_shader)


class End(Drawable):
    def __init__(self):
        pass

    def draw(self, window: Window, width, height, x=0, y=0):
        draw_texture(width, height, x, y, end_sprite, button_shader)


def draw_texture(width, height, x, y, img, shader=sprite_shader):
    texture = img.get_texture()

    vlist = pyglet.graphics.vertex_list(
        4,
        ('v2f', [0, 0, 1, 0, 0, -1, 1, -1]),
        ('t2f', [0, 0, 1, 0, 0, 1, 1, 1])
    )

    with sprite_shader:
        gl.glPushMatrix()
        gl.glTranslatef(x, y, 0)
        gl.glScalef(width, height, 0)

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)
        gl.glUniform1i(
            gl.glGetUniformLocation(sprite_shader.program, "texture".encode("ascii")),
            0
        )

        vlist.draw(gl.GL_TRIANGLE_STRIP)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glPopMatrix()
