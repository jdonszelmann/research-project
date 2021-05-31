import copy
import itertools
from collections import defaultdict, deque
import time
from typing import List, Iterator, Optional, Dict, Iterable, Set, Tuple

from mapfmclient import MarkedLocation
from tqdm import tqdm

from python.agent import UncalculatedAgent, Agent
from python.astar.no_solution import NoSolutionError
from python.coord import Coord
from python.mstar.bfsnode import BFSNode
from python.mstar.identifier import Identifier
from python.mstar.state import State
from python.mstar.statecache import StateCache
from python.mstar.visualizer import Visualizer
from python.priority_queue.fast_contains import FastContainsPriorityQueue


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


class PrematchMStar:
    directions = [Coord(0, 0), Coord(0, -1), Coord(0, 1), Coord(1, 0), Coord(-1, 0)]

    def __init__(self, grid, starts: List[MarkedLocation], goals: List[MarkedLocation], width: int, height: int):
        self.grid = grid
        self.width = width
        self.height = height
        self.starts = starts
        self.goals = goals

        self.width = width
        self.height = height

        self.joint_policy_graphs: Dict[Coord, Dict[Coord, BFSNode]] = None

        self.v_len = len(starts)
        self.state_cache: StateCache = StateCache()

        self.init_joint_policy_graphs(self.starts, self.goals)

    def init_joint_policy_graphs(self, starts: List[MarkedLocation], goals: List[MarkedLocation]):
        """Performs BFS for each agent and stores the result
            in a dictionary. """
        assert type(starts) == list, Exception("start parameter has to be list")
        assert type(goals) == list, Exception("end parameter has to be list")
        assert len(starts) == len(goals), Exception("start and end positions have to be of same length")

        self.joint_policy_graphs = {}
        for goal in goals:
            self.joint_policy_graphs[Coord(goal.x, goal.y)] = self.BFS(Coord(goal.x, goal.y))

    def wall_at(self, coord: Coord) -> bool:
        return self.grid[coord.y][coord.x] == 1

    def BFS(self, start_pos: Coord) -> dict[Coord, BFSNode]:
        visited = {}
        q = deque()
        start_node = BFSNode(start_pos, 0, None)
        q.append(start_node)

        while len(q) != 0:
            curr = q.popleft()
            if not curr.pos in visited:
                visited[curr.pos] = curr
                for n in self.get_empty_neighbours(curr.pos):
                    if n not in visited:
                        q.append(BFSNode(n, curr.move_cost + 1, curr.pos))
        return visited

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

    def search_matchings(self, od=False, visualizer: Optional[Visualizer] = None):
        shortest_path = None
        shortest_path_cost = None

        matchings_lst = list(matchings(self.starts, self.goals))

        for i in tqdm(matchings_lst, disable=True):
            best_case_cost = self.best_case_path(i)
            if shortest_path_cost is not None and best_case_cost >= shortest_path_cost:
                continue

            self.state_cache.reset()

            try:
                path = self.mstar(self.starts, i, od=od, visualizer=visualizer)
                if shortest_path is None or len(shortest_path) > len(path):
                    shortest_path = path
                    shortest_path_cost = self.path_cost(path)
                    # print(f"found with cost {shortest_path_cost}")

            except NoSolutionError:
                print("no solution")
                pass

        if shortest_path is None:
            raise NoSolutionError
        else:
            return shortest_path

    def mstar(self,
              start_pos: list[MarkedLocation],
              goal_pos: list[MarkedLocation],
              od=False,
              visualizer: Optional[Visualizer] = None):
        pq = FastContainsPriorityQueue()
        start_identifier = Identifier.from_marked_locations(start_pos)
        goal_identifier = Identifier.from_marked_locations(goal_pos)

        start_state = self.state_cache.get(start_identifier)
        start_state.cost = 0
        start_state.heuristic = self.heuristic(start_state.identifier, goal_pos)
        pq.enqueue(start_state)

        if od:
            expand_function = self.expand_OD
        else:
            expand_function = self.expand_joint_actions

        start = time.time()

        while not pq.empty():
            curr: State = pq.dequeue()
            if curr.identifier == goal_identifier:
                if visualizer is not None:
                    visualizer.end_sim()

                return curr.backtrack()

            print(curr)

            if visualizer is not None:
                visualizer.submit_state(curr)
                start = time.time()
                print(f"start expand at t=0")

            expansion = expand_function(curr, goal_pos, debug=visualizer is not None)
            if visualizer is not None:
                print(f"expanded {len(expansion)} nodes at t={time.time() - start}")

            # print("expansion:")
            for new_identifier in expansion:
                new = self.state_cache.get(new_identifier)

                if new.is_standard:
                    col = self.collisions(curr.identifier.actual, new.identifier.actual)

                    new.add_back_set(curr)
                    new.merge_collision_sets(col)

                    # if visualizer is not None:
                    #   print(f"start backprop at t={time.time() - start}")
                    if curr.is_standard:
                        self.backprop(curr, new.collision_set, pq, goal_pos)
                    else:
                        p = curr
                        while p is not None and not p.is_standard:
                            p = p.parent

                        if p is not None:
                            self.backprop(p, new.collision_set, pq, goal_pos)
                    # if visualizer is not None:
                    #    print(f"end backprop at t={time.time() - start}")
                else:
                    col = []

                if (len(col) == 0 or not new.is_standard) and \
                        curr.cost + (cost := self.get_move_cost(goal_identifier, curr, new)) < new.cost:
                    new.cost = curr.cost + cost

                    new.heuristic = self.heuristic(new.identifier, goal_pos)
                    new.parent = curr

                    # print("insert with:")
                    # print(f"cost: {new.cost}, heur: {new.heuristic}")

                    pq.enqueue(new)
                else:
                    pass
                    # print("no insert (col)")

            if visualizer is not None:
                print(f"end expand at t={time.time() - start}")

        if visualizer is not None:
            visualizer.end_sim()

        raise NoSolutionError

    def backprop(self, v_k: State, c_l, pq, goal_pos: List[MarkedLocation]):
        self.iterative_backprop(v_k, c_l, pq, goal_pos)
        # if v_k.is_standard:
        #     if not c_l.issubset(v_k.collision_set):
        #         v_k.merge_collision_sets(c_l)
        #         if v_k not in pq:
        #             v_k.heuristic = self.heuristic(v_k.identifier, goal_pos)
        #             pq.enqueue(v_k)
        #         for v_m in v_k.get_back_set():
        #             self.backprop(v_m, v_k.collision_set, pq, goal_pos)

    def iterative_backprop(self, parent_state: State, current_collision_set, pq, goal_pos: List[MarkedLocation]):
        todo = [(parent_state, current_collision_set)]

        while len(todo) != 0:
            (parent_state, current_collision_set) = todo.pop()

            if parent_state.is_standard:
                if not current_collision_set.issubset(parent_state.collision_set):
                    parent_state.merge_collision_sets(current_collision_set)
                    if parent_state not in pq:
                        parent_state.heuristic = self.heuristic(parent_state.identifier, goal_pos)
                        pq.enqueue(parent_state)
                    for v_m in parent_state.get_back_set():
                        todo.append((v_m, parent_state.collision_set))

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

    def expand_OD(self, state: State, goal_pos: List[MarkedLocation], debug=False) -> List[Identifier]:
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
                    n_pos = self.get_next_joint_policy_position(i, p, goal_pos)
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
            n_pos = self.expand_position(i, actual_pos, goal_pos)
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

    def expand_joint_actions(self, state: State, goal_pos: List[MarkedLocation], debug=False) -> Iterable[Identifier]:
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
                res = self.expand_position(i, p, goal_pos)
            else:
                res = self.get_next_joint_policy_position(i, p, goal_pos)

            all_positions.append(res)

        if debug:
            print(all_positions)
            print(f"Calculating joint positions at {time.time() - start}")
        joint_positions = itertools.product(*all_positions)

        if debug:
            print(f"Calculating ids at {time.time() - start}")

        next_v_id = []
        for j_pos in joint_positions:
            j_pos: Tuple[Agent, ...]
            next_v_id.append(Identifier(j_pos, j_pos))

        if debug:
            print(f"found expansion of size {len(next_v_id)} at {time.time() - start}")

        return next_v_id

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

    def expand_position(self, agent_id: int, agent: Agent, goal_pos: List[MarkedLocation]):
        agent_goal = self.goal_for(agent_id, goal_pos)

        assert agent_goal in self.joint_policy_graphs

        graph = self.joint_policy_graphs[agent_goal]
        assert len(graph) != 0

        next_positions = (agent.location + d for d in self.directions)
        neighbours = [
            agent.with_new_position(n_pos)
            for n_pos in next_positions
            if n_pos in graph
        ]
        return neighbours
