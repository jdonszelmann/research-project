import itertools
from typing import Iterator
from math import sin, cos, radians

import pygame
from pygame import gfxdraw
import imageio
from tqdm import tqdm


def lerp(val, srclow, srcup, destlow, destup):
    return (val - srclow) / (srcup - srclow) * (destup - destlow) + destlow


def Move(rotation, steps, position):
    x_pos = cos(radians(rotation)) * steps + position[0]
    y_pos = sin(radians(rotation)) * steps + position[1]
    return x_pos, y_pos


def DrawThickLine(surface, point1, point2, thickness, color):
    from math import degrees, atan2
    angle = degrees(atan2(point1[1] - point2[1], point1[0] - point2[0]))

    vertices = list()
    vertices.append(Move(angle - 90, thickness, point1))
    vertices.append(Move(angle + 90, thickness, point1))
    vertices.append(Move(angle + 90, thickness, point2))
    vertices.append(Move(angle - 90, thickness, point2))

    gfxdraw.aapolygon(surface, vertices, color)
    gfxdraw.filled_polygon(surface, vertices, color)


def matchings(indices: list[int]) -> Iterator[list[int]]:
    yield from itertools.permutations(indices)


def recolor(img, color):
    w, h = img.get_size()
    r, g, b = color
    for x in range(w):
        for y in range(h):
            a = img.get_at((x, y))[3]
            img.set_at((x, y), pygame.Color(r, g, b, a))

    return img


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
black = (0, 0, 0)

clock = pygame.time.Clock()

images = []

goal_img = pygame.image.load("goal.png").convert_alpha()
goal_imgs = {
    i: pygame.transform.scale(recolor(goal_img, i), (int(node_size * 2), int(node_size * 2)))
    for i in tqdm(colors[:2])
}

goal = 0
progress = 0
timesteps = 20

last = False
ag = None

starts = list(range(n))
while goal < n + 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)

    window.fill(bg)

    if not last:
        ag = goal

    g = None
    for i in range(n):
        y = (height * i / n) + (height / n / 2)
        x1 = node_size + (width / 8)
        if i == ag:
            g = (x1, y)

        window.blit(goal_imgs[colors[1]], (x1 - node_size, y - node_size))

    assert g is not None
    s = (width - node_size, height / 2)

    ax = lerp(progress, 0, timesteps, s[0], g[0])
    ay = lerp(progress, 0, timesteps, s[1], g[1])

    if last:
        DrawThickLine(window, s, (ax, ay), 3, colors[4])

    pygame.draw.rect(window, colors[1], (s[0] - node_size / 2, s[1] - node_size / 2, node_size, node_size))
    pygame.draw.circle(window, black, (ax, ay), (node_size * 0.5) + 1)
    pygame.draw.circle(window, colors[1], (ax, ay), (node_size * 0.5))

    pygame.display.flip()

    data = pygame.surfarray.array3d(window)
    data = data.swapaxes(0, 1)
    images.append(data)

    clock.tick(20)

    if progress >= timesteps:
        progress = 0
        goal += 1
    else:
        progress += 1

    if goal >= n:
        last = True
        ag = int(n / 2)

imageio.mimsave('output.gif', images, fps=20)
