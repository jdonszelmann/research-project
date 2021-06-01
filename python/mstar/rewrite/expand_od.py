from __future__ import annotations

from typing import Iterable
from python.mstar.rewrite.config import Config
from python.mstar.rewrite.agent import Agent
from python.mstar.rewrite.collisionset import RecursiveCollisionSet
from python.mstar.rewrite.recurse import optimal_policy
from python.mstar.rewrite.state import State
from python.mstar.rewrite.identifier import Identifier
from python.mstar.rewrite.expand import expand_position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from python.mstar.rewrite.find_path_params import FindPathParams



def expand_od(
        cfg: Config,
        curr_state: State,
        params: FindPathParams
) -> Iterable[Identifier]:
    next_partial = []

    if curr_state.is_standard:
        if cfg.recursive:
            assert isinstance(curr_state.collision_set, RecursiveCollisionSet)
            assert params.state_cache_cache is not None

            next_partial_table: dict[int, Agent] = {i.index: i for i in curr_state.identifier.actual}
            all_ids = frozenset(i.index for i in curr_state.identifier.actual)
            all_colliding_ids = frozenset()

            for disjoint_collision_group in curr_state.collision_set.groups():
                if len(disjoint_collision_group) == len(all_ids):
                    # there's only one disjoint collision set
                    assert curr_state.collision_set.num_groups() == 1
                    assert disjoint_collision_group == all_ids

                    for i in all_ids:
                        next_partial_table[i] = next_partial_table[i].make_uncalculated()

                    all_colliding_ids = all_ids
                else:
                    # recurse
                    res = optimal_policy(
                        disjoint_collision_group,
                        curr_state.identifier.actual,
                        params
                    )
                    # if res is None:
                    #     return []


                    for k, v in res.items():
                        next_partial_table[k] = v

                    all_colliding_ids = all_colliding_ids.union(disjoint_collision_group)

            non_colliding_agents = all_ids.difference(all_colliding_ids)

            for d in non_colliding_agents:
                for k, val in optimal_policy(
                        frozenset((d, )),  # just one agent in the collision set, aka not colliding with anything else
                        curr_state.identifier.actual,
                        params
                ).items():
                    next_partial_table[k] = val
            next_partial = list(next_partial_table.values())

        else:
            # we're at a standard node, make a new partial node
            for agent in curr_state.identifier.partial:
                agent: Agent
                if curr_state.collision_set.contains_agent(agent):
                    next_partial.append(agent.make_uncalculated())
                else:
                    next_partial.append(params.optimal_path.best_move(agent)[-1])
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
        new_agent_positions = expand_position(actual_pos, params.grid)

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
            if any(i.is_uncalculated() for i in next_state) else
            tuple(next_state)
        )

        for next_state in next_states
    ]
