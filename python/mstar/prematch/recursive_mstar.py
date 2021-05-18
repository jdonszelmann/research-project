import copy
import itertools
from collections import defaultdict, deque
import time
from typing import List, Iterator, Optional, Dict, Iterable, Set, Tuple, Union, Callable

from mapfmclient import MarkedLocation

from python.agent import UncalculatedAgent, Agent
from python.astar.no_solution import NoSolutionError
from python.coord import Coord
from python.mstar.identifier import Identifier
from python.mstar.prematch.mstar import PrematchMStar
from python.mstar.state import State
from python.mstar.visualizer import Visualizer
from python.priority_queue.fast_contains import FastContainsPriorityQueue


class RecursiveState(State):
    def __init__(self, *args, **kwargs):
        self.child = None

        super().__init__(*args, **kwargs)

        self.collision_set: frozenset[frozenset[int]] = frozenset()

    def reset(self):
        self.child = None
        super().reset()

    def set_children(self):
        curr = self
        while curr.child is not None:
            par = curr.parent
            par.child = curr
            curr = par

    @staticmethod
    def _make_set_of_sets(original: Union[frozenset[int], frozenset[frozenset[int]]]) -> Iterable[frozenset[int]]:
        new: list[frozenset[int]] = []
        for i in original:
            if type(i) == frozenset:
                i: frozenset
                new.append(i)
                print("frozenset in other collision set?")
                breakpoint()
            else:
                return original,
        return new

    def is_collision_subset(self, other_set) -> bool:
        other_set2 = self._make_set_of_sets(other_set)

        other_set_dict = {other: False for other in other_set2}
        for k in other_set_dict.keys():
            for sub in self.collision_set:
                if k.issubset(sub):
                    other_set_dict[k] = True

        return all(list(other_set_dict.values()))

    def merge_collision_sets(self, other_collision_set: frozenset[int]):
        other_collision_set_2: list[frozenset[int]] = list(self._make_set_of_sets(other_collision_set))

        assert self.valid_collision_set()
        for other_collision_set in other_collision_set_2:
            to_merge = []
            keep_same = []
            for i in other_collision_set:
                # TODO: halve?
                for existing_set in self.collision_set:
                    if i in existing_set:
                        # TODO: make set?
                        if existing_set not in to_merge:
                            to_merge.append(existing_set)
                    else:
                        keep_same.append(existing_set)
            to_merge.append(other_collision_set)
            # remove sets in keep_same which is also in to_marge
            keep_same = [i for i in keep_same if i not in to_merge]
            big_set = frozenset(
                i
                for item in to_merge
                for i in item
            )

            self.collision_set = frozenset(
                itertools.chain([big_set], (k for k in keep_same))
            )

    def valid_collision_set(self) -> bool:
        try:
            assert False
        except AssertionError:
            pass
        else:
            # noinspection PyUnreachableCode
            return True

        temp = dict()
        flag = True
        for item in self.collision_set:
            if type(item) == frozenset:
                for it in item:
                    if not it in temp:
                        temp[it] = it
                    else:
                        flag = False
            else:
                raise Exception("invalid object type in collision set")
        return flag


def matchings(starts: List[MarkedLocation], goals: List[MarkedLocation]) -> Iterator[List[MarkedLocation]]:
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


class RecursivePrematchMStar(PrematchMStar):
    directions = [Coord(0, 0), Coord(0, -1), Coord(0, 1), Coord(1, 0), Coord(-1, 0)]

    def __init__(self, *args, sub_graphs=None, **kwargs):
        super().__init__(*args, *kwargs)

    def get_neighbours(self, position: Coord) -> Iterable[Coord]:
        for i in self.directions:
            n = i + position
            if not n.out_of_bounds(self.width, self.height):
                yield n

    def get_empty_neighbours(self, position: Coord) -> Iterable[Coord]:
        return filter(lambda i: not self.wall_at(i), self.get_neighbours(position))

    def best_case_path(self, goals: List[MarkedLocation]):
        value = 0
        for index, s in enumerate(self.starts):
            value += self.joint_policy_graphs[self.goal_for(index, goals)][Coord(s.x, s.y)].move_cost

        return value

    @staticmethod
    def path_cost(path: List[State]):
        return path[-1].cost

    def mstar(self,
              start_pos: Union[List[MarkedLocation], Identifier, Tuple[MarkedLocation, ...]],
              goal_pos: Union[List[MarkedLocation], Identifier, Tuple[MarkedLocation, ...]],
              od=True,
              visualizer: Optional[Visualizer] = None,
              end_dict: Optional[dict[int, MarkedLocation]] = None,
              sub_graphs: Optional[dict] = None,
              ):
        if end_dict is None:
            end_dict: dict[int, MarkedLocation] = {i: v for i, v in enumerate(goal_pos)}

        sub_graphs: dict[tuple[int, ...], Callable] = self.init_subgraphs(end_dict, sub_graphs)

        pq = FastContainsPriorityQueue()

        if isinstance(start_pos, list) or isinstance(start_pos, tuple):
            start_identifier = Identifier.from_marked_locations(start_pos)
        else:
            start_identifier = start_pos
        if isinstance(goal_pos, list) or isinstance(goal_pos, tuple):
            goal_identifier = Identifier.from_marked_locations(goal_pos)
        else:
            goal_identifier = goal_pos

        start_state = self.state_cache.get(start_identifier, RecursiveState)
        start_state.cost = 0
        start_state.heuristic = self.heuristic(start_state.identifier, goal_pos)
        pq.enqueue(start_state)

        if od:
            expand_function = self.expand_rOD
        else:
            raise NotImplemented
            # expand_function = self.expand_joint_actions

        start = time.time()

        while not pq.empty():
            curr: RecursiveState = pq.dequeue()
            if curr.identifier == goal_identifier:
                if visualizer is not None:
                    visualizer.end_sim()

                curr.set_children()
                return curr.backtrack()
            elif curr.child is not None:
                curr.set_children()
                cntr = 0
                while curr.child is not None:
                    curr = curr.child
                    cntr += 1
                    # TODO: why?
                    assert cntr < 50000

                assert curr.identifier == goal_identifier
                return curr.backtrack()

            if visualizer is not None:
                visualizer.submit_state(curr)
                start = time.time()
                print(f"start expand at t=0")

            expansion = expand_function(
                curr,
                goal_pos,
                end_dict,
                sub_graphs,
                od,
                visualizer,
            )
            if visualizer is not None:
                print(f"expanded {len(expansion)} nodes at t={time.time() - start}")

            for new_identifier in expansion:
                new: RecursiveState = self.state_cache.get(new_identifier, constructor=RecursiveState)

                if new.is_standard:
                    col = self.collisions(curr.identifier.actual, new.identifier.actual)

                    new.add_back_set(curr)
                    new.merge_collision_sets(col)

                    if curr.is_standard:
                        self.backprop(curr, new.collision_set, pq, goal_pos)
                    else:
                        p = curr
                        while p is not None and not p.is_standard:
                            p = p.parent

                        if p is not None:
                            self.backprop(p, new.collision_set, pq, goal_pos)
                else:
                    col = []

                if (len(col) == 0 or not new.is_standard) and \
                        curr.cost + (cost := self.get_move_cost(goal_identifier, curr, new)) < new.cost:
                    new.cost = curr.cost + cost

                    new.heuristic = self.heuristic(new.identifier, goal_pos)
                    new.parent = curr

                    pq.enqueue(new)
                else:
                    pass

            if visualizer is not None:
                print(f"end expand at t={time.time() - start}")

        if visualizer is not None:
            visualizer.end_sim()

        raise NoSolutionError

    def backprop(self, v_k, c_l, pq, goal_pos: List[MarkedLocation]):
        if v_k.is_standard:
            if not c_l.issubset(v_k.collision_set):
                v_k.merge_collision_sets(c_l)
                if not v_k in pq:
                    v_k.heuristic = self.heuristic(v_k.identifier, goal_pos)
                    pq.enqueue(v_k)
                for v_m in v_k.get_back_set():
                    self.backprop(v_m, v_k.collision_set, pq, goal_pos)

    def goal_for(self, agent_id, goal_pos: List[MarkedLocation]) -> Coord:
        ml = goal_pos[agent_id]
        return Coord(ml.x, ml.y)

    def get_shortest_path_cost(self, agent_id, location: Agent, goal_pos: List[MarkedLocation]):
        v = self.joint_policy_graphs[self.goal_for(agent_id, goal_pos)]
        c = v[location.location].move_cost
        return c

    def heuristic(self, identifier: Identifier, goal_pos: List[MarkedLocation]) -> int:
        total_cost = 0
        for i, pos in enumerate(identifier.partial):
            # TODO: probably for OD
            if pos == UncalculatedAgent:
                total_cost += self.get_shortest_path_cost(i, identifier.actual[i], goal_pos)
            else:
                total_cost += self.get_shortest_path_cost(i, pos, goal_pos)

        return total_cost

    @classmethod
    def collisions(cls, old_state: list[Agent], new_state: list[Agent]) -> frozenset[int]:
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

        return frozenset(res)

    def expand_rOD(self,
                   state: RecursiveState,
                   goal_pos: List[MarkedLocation],
                   end_dict,
                   sub_graphs,
                   od = True,
                   visualizer = None,
                   ) -> List[Identifier]:
        if state.is_standard:
            collision_set = state.collision_set
            next_tup = {i: None for i in range(self.v_len)}
            this_all_ids = frozenset(i for i in range(self.v_len))
            for c in collision_set:
                if len(c) == len(self.goals):
                    assert len(collision_set) == 1
                    assert c == this_all_ids
                    for i in this_all_ids:
                        next_tup[i] = UncalculatedAgent
                else:
                    n_p = self.query_sub_graph_optimal_policy(
                        c,
                        state.identifier.partial,
                        end_dict,
                        sub_graphs,
                        od,
                        visualizer,
                    )
                    hldr = set([i for i in c])
                    hldr2 = set(n_p.keys())
                    assert hldr == hldr2
                    for k, val in n_p.items():
                        assert next_tup[k] is None
                        next_tup[k] = val

            all_col_ids = frozenset(
                c2
                for c in collision_set
                for c2 in c
            )
            diff = this_all_ids.difference(all_col_ids)

            # Get next shortest path position for non-colliding agents
            for d in diff:
                n_pos = self.query_sub_graph_optimal_policy(
                    d,
                    state.identifier.partial,
                    end_dict,
                    sub_graphs,
                    od,
                    visualizer
                )
                for k, val in n_pos.items():
                    assert next_tup[k] is None
                    next_tup[k] = val
            next_partial = list(next_tup.values())
            assert None not in next_partial
        else:
            next_partial = list(state.identifier.partial)

        # Deterimine intermediate node level
        last_partial_index = None
        i = 0
        for i, p in enumerate(next_partial):
            if p == UncalculatedAgent:
                last_partial_index = i
                break

        next_states = []
        if last_partial_index is not None:
            # if not a standard vertex
            pos = state.identifier.actual[last_partial_index]
            positions_taken = [p for p in next_partial if p != UncalculatedAgent]
            n_pos = self.expand_position(i, pos, goal_pos)
            valid_n_pos = (
                p
                for p in n_pos
                if p not in positions_taken
            )

            once = False
            for p in valid_n_pos:
                once = True
                next_partial[last_partial_index] = p
                next_states.append(tuple(next_partial))
            if not once:
                return []
        else:
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

    def get_next_joint_policy_position(self, agent_id, agent: Agent, goal_pos: List[MarkedLocation]) -> List[Agent]:
        """Returns the shortest path next position for an agent"""
        agent_goal = self.goal_for(agent_id, goal_pos)

        assert agent_goal in self.joint_policy_graphs

        graph = self.joint_policy_graphs[agent_goal]
        assert len(graph) != 0

        next_positions = [agent.location + d for d in self.directions]

        assert agent.location in graph

        next_position_costs = {}
        for n_pos in next_positions:
            if n_pos in graph:
                cost = graph[n_pos].move_cost
                if cost not in next_position_costs:
                    next_position_costs[cost] = n_pos

        min_cost = min(next_position_costs.keys())
        min_cost_next_pos = next_position_costs[min_cost]
        return [agent.with_new_position(min_cost_next_pos)]

    def get_move_cost(self, goal_identifier: Identifier, old_state: State, new_state: State):
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
                for end, old_agent, new_agent in zip(
                        goal_identifier.actual,
                        old_state.identifier.partial,
                        new_state.identifier.partial
                ):
                    if old_agent == end and new_agent == end:
                        num_agents_stay_on_goal += 1

                cost -= num_agents_stay_on_goal
                assert cost >= 0
            else:
                # vk should be root node of vn
                assert old_state.identifier.actual == new_state.identifier.actual
                cnt_vn = 0
                for end, old_agent, new_agent in zip(
                        goal_identifier.actual,
                        old_state.identifier.partial,
                        new_state.identifier.partial
                ):
                    if not new_agent == UncalculatedAgent:
                        if old_agent == end and new_agent == end:
                            cnt_vn += 0
                        else:
                            cnt_vn += 1
                cost = cnt_vn
        else:
            if new_state.is_standard:
                num_pos_changed = 0
                cost = 0
                for end, old_agent, new_agent, pk_root in zip(
                        goal_identifier.actual,
                        old_state.identifier.partial,
                        new_state.identifier.partial,
                        old_state.identifier.actual
                ):
                    if old_agent == UncalculatedAgent:
                        assert new_agent != UncalculatedAgent
                        num_pos_changed += 1
                        if old_agent == end and new_agent == end:
                            cost += 0
                        else:
                            cost += 1
                assert num_pos_changed == 1
            else:
                num_pos_changed = 0
                cost = 0
                for end, old_agent, new_agent, pk_root in zip(
                        goal_identifier.actual,
                        old_state.identifier.partial,
                        new_state.identifier.partial,
                        old_state.identifier.actual,
                ):
                    if old_agent == UncalculatedAgent and not new_agent == UncalculatedAgent:
                        num_pos_changed += 1
                        if old_agent == end and new_agent == end:
                            cost += 0
                        else:
                            cost += 1
                assert num_pos_changed == 1

        return cost

    def expand_position(self, agent_id: int, agent: Agent, goal_pos: List[MarkedLocation]) -> Iterable[Agent]:
        agent_goal = self.goal_for(agent_id, goal_pos)

        assert agent_goal in self.joint_policy_graphs

        graph = self.joint_policy_graphs[agent_goal]
        assert len(graph) != 0

        next_positions = (agent.location + d for d in self.directions)
        return (
            agent.with_new_position(n_pos)
            for n_pos in next_positions
            if n_pos in graph
        )

    def init_subgraphs(self, end_dict: dict[int, MarkedLocation], sub_graphs: Optional[dict[tuple[int, ...], Callable]] = None):
        hldr = list(end_dict.keys())
        hldr.sort()
        own_id = tuple(hldr)
        if sub_graphs is None:
            sub_graphs = {}
        if own_id not in sub_graphs:
            sub_graphs[own_id] = self.retrieve_next_optimal_pos
        return sub_graphs

    def query_sub_graph_optimal_policy(self,
                                       this_graph_sub_identifier,
                                       sub_start_state,
                                       end_dict: dict[int, MarkedLocation],
                                       sub_graphs: dict[tuple[int, ...], Callable],
                                       od=True,
                                       visualizer=None
                                       ):
        """
        this_graph_sub_id the collision set in this instance of rM*.
        sub_start_v the full position tuple of the vertex which has the collision
        """
        # map this_graph_sub_id to global ids
        # create sub_start_dic and sub_end_dict
        # get next sub_graph position
        # map next_sub_graph position back to dict with keys of this_sub_graph_id
        if type(this_graph_sub_identifier) == int:
            this_graph_sub_identifier = frozenset((this_graph_sub_identifier,))
        assert type(this_graph_sub_identifier) == frozenset

        this_graph_sub_identifier = frozenset(sorted(this_graph_sub_identifier))
        true_ids = sorted(end_dict.keys())

        sub_start_dict = {true_ids[identifier]: sub_start_state[identifier] for identifier in this_graph_sub_identifier}
        sub_end_dict = {true_ids[identifier]: true_ids[identifier] for identifier in this_graph_sub_identifier}

        graph_id = tuple(sorted(sub_start_dict.keys()))
        assert graph_id == tuple(sorted(sub_end_dict.keys()))

        if graph_id not in sub_graphs:
            if len(graph_id) > 1:
                sub_graphs = self.init_subgraphs(sub_end_dict, sub_graphs)
                if graph_id not in sub_graphs:
                    print("Id is: {}  Sub end dict is: {}".format(graph_id, sub_end_dict))
                next_sub_v = sub_graphs[graph_id](sub_start_dict, sub_end_dict)
            elif len(graph_id) == 1:
                agent_id = graph_id[0]
                pos = sub_start_dict[agent_id]
                next_sub_v = {agent_id: self.get_next_joint_policy_position(agent_id, pos)[-1]}
            else:
                raise Exception("Graph id has to be len >= 1")
        else:
            # assert len(graph_id) > 1
            next_sub_v = sub_graphs[graph_id](sub_start_dict, sub_end_dict, od, visualizer)

        # map glabal keys back to relative keys:
        next_sub_v_relative_id = {}
        this_graph_sub_id_keys = [k for k in this_graph_sub_identifier]
        this_graph_sub_id_keys.sort()
        for i, val in enumerate(next_sub_v.values()):
            next_sub_v_relative_id[this_graph_sub_id_keys[i]] = val
        return next_sub_v_relative_id

    def retrieve_next_optimal_pos(self, start_dict, end_dict, od, visualizer):
        def sort_iterable(variable):
            a = list(variable)
            a.sort()
            return a

        assert type(start_dict) == dict
        assert set(start_dict.keys()) == set(end_dict.keys())
        start_tup = []
        for k in sort_iterable(start_dict.keys()):
            start_tup.append(start_dict[k])
        start_tup = tuple(start_tup)
        end_tup = []
        for k in sort_iterable(end_dict.keys()):
            end_tup.append(end_dict[k])
        end_tup = tuple(end_tup)

        start_v = Identifier(start_tup, start_tup)
        end_v = Identifier(end_tup, end_tup)
        actions = self.mstar(start_tup, end_tup, od, visualizer)
        v = self.state_cache.get(start_v, insert=False)
        next_v_tup = None
        if v.v_id == end_v:
            next_v_tup = start_v
        elif v.forward_pointer is None:
            assert actions is None
            next_v_tup = None
        else:
            next_v = v.forward_pointer
            cntr = 0 # infinite loop prevention? TODO
            while next_v is not None and not next_v.is_standard:
                next_v = next_v.forward_pointer
                cntr += 1
                if cntr > 50000:
                    raise Exception("Infinite while loop")
            if next_v is None:
                next_v_tup = None
            else:
                next_v_tup = next_v.v_id
        if next_v_tup is not None:
            assert next_v_tup[0] == next_v_tup[1]
            next_v_dict = {}
            inter_v, root_v = next_v_tup
            for k, inter_pos, root_pos in zip(sort_iterable(end_dict.keys()), inter_v, root_v):
                next_v_dict[k] = inter_pos  # (inter_pos, root_pos)
        else:
            next_v_dict = None
        return next_v_dict
