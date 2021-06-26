import itertools
from typing import Iterator
from math import sin, cos, radians

import pygame
from pygame import gfxdraw
import imageio


def Move(rotation, steps, position):
    x_pos = cos(radians(rotation)) * steps + position[0]
    y_pos = sin(radians(rotation)) * steps + position[1]
    return x_pos, y_pos


def DrawThickLine(surface, point1, point2, thickness, color):
    from math import degrees, atan2
    angle = degrees(atan2(point1[1] - point2[1], point1[0] - point2[0]))

    vertices = list()
    vertices.append(Move(angle-90, thickness, point1))
    vertices.append(Move(angle+90, thickness, point1))
    vertices.append(Move(angle+90, thickness, point2))
    vertices.append(Move(angle-90, thickness, point2))

    gfxdraw.aapolygon(surface, vertices, color)
    gfxdraw.filled_polygon(surface, vertices, color)


def matchings(indices: list[int]) -> Iterator[list[int]]:
    yield from itertools.permutations(indices)

pygame.init()

n = 3
width = 1000
height = (width / 4) * n
node_size = height / (3 * n)
window = pygame.display.set_mode((int(width), int(height)))

colors = [
    (204, 68, 82),
    (36, 97, 128),
    (128, 29, 39),
    (47, 152, 204),
    (17, 128, 42),
    (67, 204, 98),
    (57, 204, 174),
    (102, 82, 74),
    (128, 124, 23),
    (204, 111, 78),
]

bg = (0x22, 0x27, 0x2e)
line_color = (0x72, 0x31, 0x47)

clock = pygame.time.Clock()

images = []

starts = list(range(n))
for goals in matchings(starts):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)

    window.fill(bg)
    for (i, j) in zip(starts, goals):
        y1 = (height * i / n) + (height / n / 2)
        y2 = (height * j / n) + (height / n / 2)
        x1 = node_size + (width / 8)
        x2 = width - (node_size + (width / 8))

        DrawThickLine(window, (x1, y1), (x2, y2), 10, line_color)


    for i in range(n):
        y = (height * i / n) + (height / n / 2)
        x1 = node_size + (width / 8)
        x2 = width - (node_size + (width / 8))
        pygame.draw.circle(window, colors[i], (x1, y), node_size)
        pygame.draw.circle(window, colors[i], (x2, y), node_size)


    pygame.display.flip()

    data = pygame.surfarray.array3d(window)
    data = data.swapaxes(0, 1)
    images.append(data)

    clock.tick(2)

imageio.mimsave('output.gif', images, fps=2)


