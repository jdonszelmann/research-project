import sys
from heapq import heappush, heappop


def get_src_modules():
    modules = sys.modules
    srcs = []
    for i in sys.modules:
        if "src" in i:
            srcs.append(i)
    for i in srcs:
        del sys.modules[i]

    return modules


def solve_with_modules(modules, fn, *args, **kwargs):
    old = sys.modules
    sys.modules = modules
    res = fn(*args, **kwargs)
    sys.modules = old
    return res


def convert_grid_dict_ints(graph):
    grap_new = {}
    height = len(graph)
    width = len(graph[0])
    coord_to_int = {}
    int_to_coord = {}
    for i in range(len(graph)):
        for j in range(len(graph[0])):
            if graph[i][j] == 0:
                current = width * i + j
                coord_to_int[(j, i)] = current
                int_to_coord[current] = (j, i)
                neighbours = []
                if i != 0 and graph[i - 1][j] == 0:
                    neighbours.append(width * (i - 1) + j)
                if j != 0 and graph[i][j - 1] == 0:
                    neighbours.append(width * i + j - 1)
                if i != height - 1 and graph[i + 1][j] == 0:
                    neighbours.append(width * (i + 1) + j)
                if j != width - 1 and graph[i][j + 1] == 0:
                    neighbours.append(width * i + j + 1)
                grap_new[current] = neighbours
    return grap_new, coord_to_int, int_to_coord


def dijkstra_distance(G, source):
    dist = {}  # dictionary of final distances
    seen = {source: 0}
    c = 1
    fringe = []  # use heapq with (distance,label) tuples
    heappush(fringe, (0, c, source))
    while fringe:
        (d, _, v) = heappop(fringe)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        neighbours = G[v]
        for neighbour in neighbours:
            vw_dist = d + 1
            if neighbour not in seen or vw_dist < seen[neighbour]:
                seen[neighbour] = vw_dist
                c += 1
                heappush(fringe, (vw_dist, c, neighbour))
    return dist
