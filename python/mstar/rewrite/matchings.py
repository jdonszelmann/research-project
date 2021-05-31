from typing import Iterator
import copy
import itertools

from mapfmclient import MarkedLocation
from collections import defaultdict


def matchings(starts: list[MarkedLocation], goals: list[MarkedLocation]) -> Iterator[list[MarkedLocation]]:
    reordered_goals = []
    had = set()
    for i in starts:
        for index, j in enumerate(goals):
            if j.color == i.color and index not in had:
                reordered_goals.append(j)
                had.add(index)
                break
        else:
            raise ValueError(f"starts and ends of color {i.color} have a different size")

    groups = defaultdict(list)
    for index, i in enumerate(reordered_goals):
        groups[i.color].append(index)

    permutations = []
    originals = []

    for indices in groups.values():
        perm = itertools.permutations(indices)
        originals.append(indices)
        permutations.append(perm)

    product = itertools.product(*permutations)

    for i in product:
        curr = copy.copy(reordered_goals)
        for perm, o in zip(i, originals):
            for a, b in zip(perm, o):
                curr[a] = reordered_goals[b]

        yield curr
