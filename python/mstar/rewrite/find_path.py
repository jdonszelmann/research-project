from typing import Optional

from python.mstar.rewrite.find_path_params import FindPathParams
from python.mstar.rewrite.heuristic import Heuristic
from python.mstar.rewrite.state import State
from python.mstar.rewrite.expand import expand
from python.mstar.rewrite.expand_od import expand_od
from python.mstar.rewrite.goal import Goal
from python.mstar.rewrite.path import Path
from python.mstar.rewrite.collisionset import CollisionSet
from python.priority_queue.fast_contains import FastContainsPriorityQueue

from tqdm import tqdm


def find_collisions(curr_state: State, new_state: State) -> CollisionSet:
    res: list[tuple[int, int]] = []

    curr_agents = curr_state.identifier.actual
    new_agents = new_state.identifier.actual

    for a1 in range(len(curr_agents)):
        for a2 in range(min(a1, len(new_agents))):
            if new_agents[a1] == new_agents[a2]:
                res.append((new_agents[a1].index, new_agents[a2].index))

            elif curr_agents[a1] == new_agents[a2] and new_agents[a1] == curr_agents[a2]:
                res.append((new_agents[a1].index, new_agents[a2].index))

    return curr_state.collision_set.__class__.from_colliding_indices(res)


def backprop(
        curr_state: State,
        new_state: State,
        pq: FastContainsPriorityQueue,
        heuristic: Heuristic,
):
    stack: list[tuple[State, CollisionSet]] = [
        (curr_state, new_state.collision_set)
    ]

    while len(stack) != 0:
        parent_state, current_collision_set = stack.pop()

        if parent_state.is_standard and \
                not current_collision_set.subset(parent_state.collision_set):
            parent_state.merge_collision_sets(current_collision_set)
            if parent_state not in pq:
                parent_state.set_heuristic(heuristic)
                pq.enqueue(parent_state)

            for v_m in parent_state.get_back_set():
                stack.append((v_m, parent_state.collision_set))


def transition_cost(
    curr_state: State,
    new_state: State,
    num_agents: int,
    goal: Goal,
):
    """
    Cost of moving from old_state to new_state
    """

    # It is possible for old_state and new_state to both be standard nodes. Need to account for this in cost
    # Due to subdimensional expansion, expanded node neighbours are not always 1 apart.
    # eg. expanding a standard node where x agents follow individually optimal policies

    if curr_state.is_standard and new_state.is_standard:
        num_agents_stay_on_goal = 0
        for curr_agent, new_agent in zip(
                curr_state.identifier.actual,
                new_state.identifier.actual
        ):
            if goal.on_goal(curr_agent) and goal.on_goal(new_agent):
                num_agents_stay_on_goal += 1

        return num_agents - num_agents_stay_on_goal

    elif curr_state.is_standard and not new_state.is_standard:
        cost = 0
        for curr_agent, new_agent in zip(
            curr_state.identifier.partial,
            new_state.identifier.partial
        ):
            if not new_agent.is_uncalculated() and \
                    not (goal.on_goal(curr_agent) and goal.on_goal(new_agent)):
                cost += 1
        return cost
    elif not curr_state.is_standard and new_state.is_standard:
        cost = 0
        for curr_agent, new_agent, curr_agent_actual in zip(
                curr_state.identifier.partial,
                new_state.identifier.partial,
                curr_state.identifier.actual,
        ):
            if curr_agent.is_uncalculated() and \
                    not (goal.on_goal(curr_agent_actual) and goal.on_goal(new_agent)):
                cost += 1
        return cost
    else:
        cost = 0
        for curr_agent, new_agent, curr_agent_actual in zip(
                curr_state.identifier.partial,
                new_state.identifier.partial,
                curr_state.identifier.actual,
        ):
            if curr_agent.is_uncalculated() and \
                    not new_agent.is_uncalculated() and \
                    not (goal.on_goal(curr_agent_actual) and goal.on_goal(new_agent)):
                cost += 1
        return cost


def find_path(
        start: State,

        params: FindPathParams
) -> Optional[Path]:
    pq = FastContainsPriorityQueue()
    start.cost = 0
    start.set_heuristic(params.heuristic)
    pq.enqueue(start)

    while not pq.empty():
        # if not params.cfg.memory_usage_ok():
        #     tqdm.write("memory limiter")
        #     return None

        curr_state: State = pq.dequeue()

        if params.cfg.debug:
            tqdm.write(repr(curr_state))

        if params.goal.is_goal(curr_state):
            if params.cfg.recursive:
                curr_state.set_child_pointers()

            return curr_state.backtrack()

        if params.cfg.recursive and curr_state.has_child():
            curr_state.set_child_pointers()
            child = curr_state.find_deepest_child()
            assert params.goal.is_goal(child)
            return child.backtrack()


        if params.cfg.operator_decomposition:
            expansion = expand_od(params.cfg, curr_state, params)
        else:
            expansion = expand(curr_state, params)

        if params.cfg.report_expansions:
            params.cfg.report_expansion(len(list(expansion)))


        for new_identifier in expansion:
            new_state = params.state_cache.get(new_identifier)

            collisions: Optional[CollisionSet]
            if new_state.is_standard:
                collisions = find_collisions(
                    curr_state,
                    new_state
                )

                new_state.add_back_set(curr_state)
                new_state.merge_collision_sets(collisions)

                if curr_state.is_standard:
                    backprop(curr_state, new_state, pq, params.heuristic)
                else:
                    p = curr_state
                    while p is not None and not p.is_standard:
                        p = p.parent

                    if p is not None:
                        backprop(p, new_state, pq, params.heuristic)
            else:
                collisions = None


            # if collisions is not None and len(collisions) != 0:
            #     print(collisions)

            if collisions is None or len(collisions) == 0 or not new_state.is_standard:
                if curr_state.cost + (cost := transition_cost(curr_state, new_state, params.num_agents, params.goal)) < new_state.cost:
                    new_state.cost = curr_state.cost + cost
                    new_state.set_heuristic(params.heuristic)

                    new_state.parent = curr_state

                    pq.enqueue(new_state)

    return None
