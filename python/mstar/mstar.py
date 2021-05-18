from __future__ import annotations

import time
from itertools import product
from typing import Optional, List, Tuple, Set, Iterable, Iterator

from mapfmclient import MarkedLocation

from python.agent import Agent, UncalculatedAgent
from python.astar.no_solution import NoSolutionError
from python.mstar.identifier import Identifier
from python.mstar.state import State
from python.mstar.statecache import StateCache
from python.mstar.visualizer import Visualizer
from python.priority_queue.fast_contains import FastContainsPriorityQueue







class MStar:
    def __init__(self,
                 starts: List[MarkedLocation],
                 ends: List[MarkedLocation],
                 expand_position,
                 get_next_joint_policy_position,
                 get_shortest_path_cost
                 ):

        assert len(starts) == len(ends), "start and end positions have to be of same length"

        self.starts = starts
        self.ends = ends
        self.v_len = len(starts)
        # self.f_e_kl = self.v_len * 1 #cost of traversing an edge
        self.expand_position = expand_position
        self.get_next_joint_policy_position = get_next_joint_policy_position
        self.heuristic_shortest_path_cost = get_shortest_path_cost
        self.state_cache = StateCache()

    def search(self, OD=True, visualizer: Optional[Visualizer] = None) -> List[State]:
        pq = FastContainsPriorityQueue()
        start_identifier = Identifier.from_marked_locations(self.starts)

        start_state = self.state_cache.get(start_identifier)
        start_state.cost = 0
        start_state.heuristic = self.heuristic(start_state.identifier)
        pq.enqueue(start_state)

        if OD:
            expand_function = self.expand_OD
        else:
            expand_function = self.expand_joint_actions

        while not pq.empty():
            curr = pq.dequeue()

            # TODO: matching
            if self.final_state(curr):
                if visualizer is not None:
                    visualizer.end_sim()

                return curr.backtrack()

            expansion = expand_function(curr, debug=visualizer is not None)

            for new_identifier in expansion:
                # Intermediate states not part of back propagation
                # For standard states only
                new = self.state_cache.get(new_identifier)

                if new.is_standard:
                    col = self.collisions(curr.identifier.actual, new.identifier.actual)

                    new.add_back_set(curr)
                    new.merge_collision_sets(col)

                    if curr.is_standard:
                        self.backprop(curr, new.collision_set, pq)
                    else:
                        p = curr
                        while p is not None and not p.is_standard:
                            p = p.parent

                        if p is not None:
                            self.backprop(p, new.collision_set, pq)
                else:
                    col = []

                if (len(col) == 0 or not new.is_standard) and \
                        curr.cost + (cost := self.get_move_cost(curr, new)) < new.cost:
                    new.cost = curr.cost + cost

                    new.heuristic = self.heuristic(new.identifier)
                    new.parent = curr
                    pq.enqueue(new)

        if visualizer is not None:
            visualizer.end_sim()

        raise NoSolutionError

    def backprop(self, v_k, c_l, pq):
        if v_k.is_standard:
            if not c_l.issubset(v_k.collision_set):
                v_k.merge_collision_sets(c_l)
                if v_k not in pq:
                    v_k.heuristic = self.heuristic(v_k.identifier)
                    pq.enqueue(v_k)
                for v_m in v_k.get_back_set():
                    self.backprop(v_m, v_k.collision_set, pq)

    def heuristic(self, identifier: Identifier):
        total_cost = 0
        for i, pos in enumerate(identifier.partial):
            # TODO: probably for OD
            if pos == UncalculatedAgent:
                total_cost += self.heuristic_shortest_path_cost(i, identifier.actual[i])
            else:
                total_cost += self.heuristic_shortest_path_cost(i, pos)
        return total_cost

    @classmethod
    def collisions(cls, old_state: List[Agent], new_state: List[Agent]) -> Set[int]:
        """
        :param old_state: the parent state from which the new state was generated (used for edge constraints)
        :param new_state: the new state that is generated, about which we want to know if it contains collisions
        :return: A set of agent indices (TODO!)
        """

        assert len(old_state) == len(new_state)

        res = set()

        for a1 in range(len(old_state)):
            for a2 in range(min(a1, len(new_state))):
                if new_state[a1] == new_state[a2]:
                    res.add(a1)
                    res.add(a2)

                elif old_state[a1] == new_state[a2] and new_state[a1] == old_state[a2]:
                    res.add(a1)
                    res.add(a2)

        return res

    def final_state(self, state: State) -> bool:
        # implied by constraints on move
        # if self.has_double(state.agents):
        #     return False

        for agent in state.identifier.actual:
            if not self.on_final(agent):
                return False

        return True

    def on_final(self, agent: Agent) -> bool:
        for i in self.ends:
            if i.x == agent.x and i.y == agent.y and i.color == agent.color:
                return True

        return False

    def get_move_cost(self, old_state: State, new_state: State):
        """
        Cost of moving from old_state to new_state
        """
        # It is possible for old_state and new_state to both be standard nodes. Need to account for this in cost
        # Due to subdimensional expansion, expanded node neighbours are not always 1 apart.
        # eg. expanding a standard node where x agents follow individually optimal policies
        if old_state.is_standard:
            if new_state.is_standard:
                cost = self.v_len
                # count number of transitions from goal to goal pos
                num_agents_stay_on_goal = 0
                for old_agent, new_agent in zip(old_state.identifier.partial, new_state.identifier.partial):
                    if self.on_final(old_agent) and self.on_final(new_agent):
                        num_agents_stay_on_goal += 1

                cost -= num_agents_stay_on_goal
                assert cost >= 0
            else:
                # vk should be root node of vn
                assert old_state.identifier.actual == new_state.identifier.actual
                cnt_vn = 0
                for new_agent, old_agent in zip(
                        new_state.identifier.partial,
                        old_state.identifier.partial
                ):
                    if not new_agent == UncalculatedAgent:
                        if self.on_final(old_agent) and self.on_final(new_agent):  # if agent stayed on goal
                            cnt_vn += 0
                        else:
                            cnt_vn += 1
                cost = cnt_vn
        else:
            if new_state.is_standard:
                num_pos_changed = 0
                cost = 0
                for old_agent, new_agent, pk_root in zip(
                        old_state.identifier.partial,
                        new_state.identifier.partial,
                        old_state.identifier.actual
                ):
                    if old_agent == UncalculatedAgent:
                        assert new_agent != UncalculatedAgent
                        num_pos_changed += 1
                        if self.on_final(old_agent) and self.on_final(pk_root):
                            cost += 0
                        else:
                            cost += 1
                assert num_pos_changed == 1
            else:
                num_pos_changed = 0
                cost = 0
                for old_agent, new_agent, pk_root in zip(
                        old_state.identifier.partial,
                        new_state.identifier.partial,
                        old_state.identifier.actual,
                ):
                    if old_agent == UncalculatedAgent and not new_agent == UncalculatedAgent:
                        num_pos_changed += 1
                        if self.on_final(old_agent) and self.on_final(pk_root):
                            cost += 0
                        else:
                            cost += 1
                assert num_pos_changed == 1

        # assert cost >= 0  # vn should always be of higher count
        return cost

    def expand_OD(self, state: State, debug=False) -> Iterable[Identifier]:
        next_partial = []

        # TODO: not O(n)
        if UncalculatedAgent not in state.identifier.partial:
            # we're at a standard node, make a new partial node
            assert state.is_standard

            collision_set = state.collision_set
            for i, p in enumerate(state.identifier.partial):
                if i in collision_set:
                    next_partial.append(UncalculatedAgent)
                else:
                    n_pos = self.get_next_joint_policy_position(i, p, self.ends[i])
                    next_partial.append(n_pos[-1])
        else:
            # we're already at a partial node, expand it
            next_partial = list(state.identifier.partial)

        # Determine intermediate node level
        last_partial_index = None
        i = 0
        for i, p in enumerate(next_partial):
            if p == UncalculatedAgent:
                last_partial_index = i
                break

        next_states = []
        if last_partial_index is None:
            # there's no uncalculated part found, so this node must be complete
            # so next partial isn't actually partial in this case
            assert UncalculatedAgent not in next_partial
            next_states.append(tuple(next_partial))
        else:
            # if not a standard vertex
            actual_pos = state.identifier.actual[last_partial_index]
            positions_taken = [p for p in next_partial if p != UncalculatedAgent]
            # TODO: does i matter?
            n_pos = self.expand_position(i, actual_pos)
            valid_n_pos = [p for p in n_pos if p not in positions_taken]

            if len(valid_n_pos) == 0:
                return []
            for p in valid_n_pos:
                next_partial[last_partial_index] = p
                next_states.append(tuple(next_partial))

        # Make v_id's:
        v_ids = []
        for inter_v in next_states:
            inter_v: Tuple[Agent]
            if UncalculatedAgent not in inter_v:
                v_ids.append(Identifier(tuple(inter_v), tuple(inter_v)))
            else:
                v_ids.append(Identifier(tuple(inter_v), state.identifier.actual))

        return v_ids

    def expand_joint_actions(self, state: State, debug=False) -> Iterable[Identifier]:
        if debug:
            start = time.time()
            print("----------------")
            print("EXPANSION at t=0")

        assert state.is_standard, "used expand joint actions with non-standard node"

        all_positions = []
        collisions = state.collision_set

        if debug:
            print(f"finding new agent positions at {time.time() - start}")

        for i, p in enumerate(state.identifier.actual):
            if i in collisions:
                res = self.expand_position(p)
            else:
                res = self.get_next_joint_policy_position(p)

            all_positions.append(res)

        if debug:
            print(all_positions)
            print(f"Calculating joint positions at {time.time() - start}")
        joint_positions = product(*all_positions)

        if debug:
            print(f"Calculating ids at {time.time() - start}")

        next_v_id = []
        for j_pos in joint_positions:
            j_pos: Tuple[Agent]
            next_v_id.append(Identifier(j_pos, j_pos))

        if debug:
            print(f"found expansion of size {len(next_v_id)} at {time.time() - start}")

        return next_v_id
