from typing import Iterable

from python.mstar.rewrite.find_path_params import FindPathParams
from python.mstar.rewrite.agent import Agent
from python.mstar.rewrite.grid import Grid
from python.mstar.rewrite.identifier import Identifier
from python.mstar.rewrite.state import State

import itertools


def expand_position(agent: Agent, grid: Grid) -> list[Agent]:
    """
    Find all positions an agent can move to from its current position.
    Only returns positions which are not walls and are in bounds.
    """
    # TODO: verify
    return [
        agent.with_new_position(n_pos)
        for n_pos in grid.get_empty_moves(agent.location)
    ]


def expand(curr_state: State, params: FindPathParams) -> Iterable[Identifier]:
    """
    Expand a state into it's children states
    """

    per_agent_expansion = []
    for agent in curr_state.identifier.actual:
        agent: Agent

        # if an agent is colliding, expand it fully
        if curr_state.collision_set.is_colliding(agent):
            res = expand_position(agent, params.grid)

        # otherwise, expand following the individually optimal path
        else:
            res = params.optimal_path.best_move(agent)

        per_agent_expansion.append(res)

    new_identifiers = itertools.product(*per_agent_expansion)

    return [
        Identifier(part, part)
        for part in new_identifiers
    ]
