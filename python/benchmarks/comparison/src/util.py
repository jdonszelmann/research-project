from itertools import combinations
from typing import List, Optional, Tuple, Iterable, TypeVar, Callable

from src.data.agent import Agent
from src.data.conflicts import Conflict, VertexConflict, EdgeConflict
from src.data.vertex import Vertex

T = TypeVar("T")


def flatten(xss: Iterable[Iterable[T]]) -> List[T]:
    return [x for xs in xss for x in xs]


def range_incl(start: int, stop: int) -> Iterable[int]:
    return range(start, stop + 1)


def to_mapf_tuples(vs: List[Vertex]) -> List[Tuple[int, int]]:
    return [(v.x, v.y) for v in vs]


def get_vertex_at_time(path: List[Vertex], t: int) -> Vertex:
    if t >= len(path):
        return path[-1]
    else:
        return path[t]


def get_first_conflict(
    paths: Iterable[Tuple[Agent, List[Vertex]]],
    do_compare: Callable[[Agent, Agent], bool] = lambda: True,
    agent_disappears: Callable[[Vertex, Agent], bool] = lambda: False
) -> Optional[Conflict]:
    max_path_length = max([len(path[1]) for path in paths])

    for ((a_i, sol1), (a_j, sol2)) in combinations(paths, 2):
        if not do_compare(a_i, a_j):
            continue

        for t in range(max_path_length):
            v1 = get_vertex_at_time(sol1, t)
            if v1 == get_vertex_at_time(sol2, t):
                # If the agent that disappears was already there it's okay
                # If the agent that disappears only comes here now, it's not
                a_i_disappears = agent_disappears(v1, a_i)
                a_i_prev = get_vertex_at_time(sol1, t-1)

                a_j_disappears = agent_disappears(v1, a_j)
                a_j_prev = get_vertex_at_time(sol2, t-1)

                if (a_i_disappears and a_i_prev == v1) or (a_j_disappears and a_j_prev == v1):
                    continue

                return VertexConflict(v1, a_i, a_j, t)

    for ((a_i, sol1), (a_j, sol2)) in combinations(paths, 2):
        if not do_compare(a_i, a_j):
            continue

        for t in range(max_path_length):
            start_equal = get_vertex_at_time(sol1, t) == get_vertex_at_time(sol2, t + 1)
            end_equal = get_vertex_at_time(sol1, t + 1) == get_vertex_at_time(sol2, t)
            if start_equal and end_equal:
                return EdgeConflict((sol1[t], sol1[t + 1]), a_i, a_j, t + 1)

    return None
