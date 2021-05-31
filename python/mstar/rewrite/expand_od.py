from typing import Iterable

from python.mstar.rewrite.agent import Agent
from python.mstar.rewrite.state import State
from python.mstar.rewrite.identifier import Identifier
from python.mstar.rewrite.optimal_path import OptimalPath
from python.mstar.rewrite.grid import Grid
from python.mstar.rewrite.expand import expand_position


def expand_od(curr_state: State, grid: Grid, optimal_path: OptimalPath) -> Iterable[Identifier]:
    next_partial = []

    if curr_state.is_standard:
        # we're at a standard node, make a new partial node
        for agent in curr_state.identifier.partial:
            agent: Agent
            if curr_state.collision_set.contains_agent(agent):
                next_partial.append(agent.make_uncalculated())
            else:
                next_partial.append(optimal_path.best_move(agent)[-1])
    else:
        # we're already at a partial node, expand it
        next_partial = list(curr_state.identifier.partial)

    # Determine intermediate node level
    last_partial_index = None
    for i, agent in enumerate(next_partial):
        if agent.is_uncalculated():
            last_partial_index = i
            break

    next_states = []
    if last_partial_index is None:
        # there's no uncalculated part found, so this node must be complete
        # so next partial isn't actually partial in this case
        next_states.append(tuple(next_partial))
    else:
        # if not a standard vertex, take the actual position
        # of the first uncalculated agent and expand it
        actual_pos: Agent = curr_state.identifier.actual[last_partial_index]
        new_agent_positions = expand_position(actual_pos, grid)

        # make sure no other agent is partially at this partial position
        positions_taken = [p for p in next_partial if not p.is_uncalculated()]
        valid_new_agent_positions = [
            p
            for p in new_agent_positions
            if p not in positions_taken
        ]

        # none were valid, this partial expansion was useless so discard it
        if len(valid_new_agent_positions) == 0:
            return []
        for agent in valid_new_agent_positions:
            next_partial[last_partial_index] = agent
            next_states.append(tuple(next_partial))


    return [
        Identifier(
            tuple(next_state),
            curr_state.identifier.actual
        )

        if any(i.is_uncalculated() for i in next_state)
        else

        Identifier(
            tuple(next_state),
            tuple(next_state)
        )

        for next_state in next_states
    ]
