from __future__ import annotations

from typing import Optional

from python.mstar.rewrite.goal import Goal
from python.mstar.rewrite.statecache import StateCache
from python.mstar.rewrite.agent import Agent
from python.mstar.rewrite.state import State
from python.mstar.rewrite.identifier import Identifier

from python.mstar.rewrite.find_path_params import FindPathParams


def recurse_mstar(start_state: State, goal: Goal, cache: StateCache, params: FindPathParams) -> Optional[dict[int, Agent]]:
    from python.mstar.rewrite.find_path import find_path


    paths = find_path(
        start_state,
        FindPathParams(
            cfg=params.cfg,
            goal=goal,
            num_agents=len(start_state.identifier.actual),

            grid=params.grid,
            optimal_path=params.optimal_path,
            state_cache=cache,
            heuristic=params.heuristic,

            state_cache_cache=params.state_cache_cache
        )
    )


    processed_start_state = cache.get(start_state.identifier)

    optimal_policy: Optional[list[Agent]] = None

    if goal.is_goal(processed_start_state):
        optimal_policy = start_state.identifier.actual
    elif processed_start_state.child is None:
        # there was no solution
        assert paths is None

    else:
        next_state: State = processed_start_state.child
        while next_state is not None and not next_state.is_standard:
            next_state = next_state.child

        if next_state is not None:
            optimal_policy = next_state.identifier.actual

    if optimal_policy is not None:
        return {agent.index: agent for agent in optimal_policy}
    else:
        return None


def optimal_policy(disjoint_collision_group: frozenset[int],
                   agents: tuple[Agent, ...],
                   params: FindPathParams,
                   ) -> Optional[dict[int, Agent]]:

    associated_agents = tuple(agent for agent in agents if agent.index in disjoint_collision_group)

    sub_start_identifier = Identifier(associated_agents, associated_agents)

    sub_goal = params.goal.for_agents(associated_agents)

    assert len(disjoint_collision_group) == len(associated_agents)

    subgraph: dict[int, Agent]

    # print(disjoint_collision_group)

    if disjoint_collision_group in params.state_cache_cache:
        cache = params.state_cache_cache.get(disjoint_collision_group)

        sub_start_state = cache.get(sub_start_identifier)

        generated_optimal_policy = recurse_mstar(sub_start_state, sub_goal, cache, params)
    else:
        if len(disjoint_collision_group) > 1:
            # there more than one agent in this subgraph
            cache = StateCache(params.cfg, params.state_cache.constructor)
            params.state_cache_cache.add(disjoint_collision_group, cache)

            sub_start_state = cache.get(sub_start_identifier)

            generated_optimal_policy = recurse_mstar(sub_start_state, sub_goal, cache, params)

        elif len(disjoint_collision_group) == 1:
            generated_optimal_policy = {
                associated_agents[0].index: params.optimal_path.best_move(associated_agents[0])[-1]
            }

        else:
            raise Exception("subgraph id must have length of at least 1")

    return generated_optimal_policy
