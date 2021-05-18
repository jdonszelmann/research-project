import itertools
from collections import defaultdict
from math import inf
from typing import List, Optional, Iterable, Set, Tuple

from mapfmclient import MarkedLocation

from python.agent import UncalculatedAgent, Agent
from python.astar.no_solution import NoSolutionError
from python.coord import Coord
from python.mstar.bfsnode import BFSNode
from python.mstar.identifier import Identifier
from python.mstar.prematch.mstar import PrematchMStar
from python.mstar.state import State
from python.mstar.visualizer import Visualizer
from python.priority_queue.fast_contains import FastContainsPriorityQueue


class MatchingMStar(PrematchMStar):
    def __init__(self, grid, starts: List[MarkedLocation], goals: List[MarkedLocation], width: int, height: int):
        super().__init__(grid, starts, goals, width, height)

        self.per_color_joint_policy_graphs: dict[int, list[dict[Coord, BFSNode]]] = \
            self.init_per_color_joint_policy_graphs(starts, goals)

    def init_joint_policy_graphs(self, starts: List[MarkedLocation], goals: List[MarkedLocation]):
        # skip this, normal matching MStar uses per-color joint policy graphs
        pass

    def init_per_color_joint_policy_graphs(self,
                                           starts: List[MarkedLocation],
                                           ends: List[MarkedLocation]) -> dict[int, list[dict[Coord, BFSNode]]]:
        """Performs BFS for each agent and stores the result
            in a dictionary. """
        assert type(starts) == list, Exception("start parameter has to be list")
        assert type(ends) == list, Exception("end parameter has to be list")
        assert len(starts) == len(ends), Exception("start and end positions have to be of same length")

        joint_policy_graphs = defaultdict(list)
        for (start, goal) in zip(starts, ends):
            joint_policy_graphs[goal.color].append(self.BFS(Coord(goal.x, goal.y)))
        return joint_policy_graphs


    def search_matchings(self, od=False, visualizer: Optional[Visualizer] = None):
        return self.mstar(self.starts, self.goals, od, visualizer)

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

        while not pq.empty():
            curr: State = pq.dequeue()
            if self.final_state(curr):
                if visualizer is not None:
                    visualizer.end_sim()

                return curr.backtrack()

            if visualizer is not None:
                visualizer.submit_state(curr)

            expansion = expand_function(curr, goal_pos, debug=visualizer is not None)

            for new_identifier in expansion:
                new = self.state_cache.get(new_identifier)

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

        if visualizer is not None:
            visualizer.end_sim()

        raise NoSolutionError

    def get_matching_shortest_path_cost(self, agent: Agent):
        smallest = inf
        for i in self.per_color_joint_policy_graphs[agent.color]:
            c = i[agent.location].move_cost
            if c < smallest:
                smallest = c

        return smallest

    def heuristic(self, identifier: Identifier, goal_pos: List[MarkedLocation]) -> int:
        total_cost = 0
        for i, pos in enumerate(identifier.partial):
            if pos == UncalculatedAgent:
                total_cost += self.get_matching_shortest_path_cost(identifier.actual[i])
            else:
                total_cost += self.get_matching_shortest_path_cost(pos)

        return total_cost

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
                    n_pos = self.get_next_matching_joint_policy_position(p)
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
            n_pos = self.expand_position_matching(actual_pos)
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
        assert state.is_standard, "used expand joint actions with non-standard node"

        all_positions = []
        collisions = state.collision_set


        for i, p in enumerate(state.identifier.actual):
            if i in collisions:
                res = self.expand_position_matching(p)
            else:
                res = self.get_next_matching_joint_policy_position(p)

            all_positions.append(res)

        joint_positions = itertools.product(*all_positions)

        next_v_id = []
        for j_pos in joint_positions:
            j_pos: Tuple[Agent, ...]
            next_v_id.append(Identifier(j_pos, j_pos))

        return next_v_id

    def get_next_matching_joint_policy_position(self, agent: Agent) -> List[Agent]:
        """Returns the shortest path next position for an agent"""
        assert agent.color in self.per_color_joint_policy_graphs

        same_color_graphs = self.per_color_joint_policy_graphs[agent.color]
        assert len(same_color_graphs) != 0

        next_positions = [agent.location + d for d in self.directions]

        chosen = set()

        for this_graph in same_color_graphs:
            assert agent.location in this_graph

            next_position_costs = {}
            for n_pos in next_positions:
                if n_pos in this_graph:
                    cost = this_graph[n_pos].move_cost
                    if cost not in next_position_costs or next_position_costs[cost] not in chosen:
                        next_position_costs[cost] = n_pos

            curr_min_cost = min(next_position_costs.keys())
            curr_min_cost_next_pos = next_position_costs[curr_min_cost]

            chosen.add(curr_min_cost_next_pos)

        # print(len(chosen))
        return [agent.with_new_position(i) for i in chosen]

    def expand_position_matching(self, agent: Agent):
        """Returns a list of possible next positions for an agent (ignoring other agents) """
        assert agent.color in self.per_color_joint_policy_graphs
        this_color_graphs = self.per_color_joint_policy_graphs[agent.color]

        next_positions = (agent.location + d for d in self.directions)
        neighbours = [
            agent.with_new_position(n_pos)
            for n_pos in next_positions
            if any(n_pos in i for i in this_color_graphs)
        ]
        return neighbours

    def final_state(self, state: State) -> bool:
        # implied by constraints on move
        # if self.has_double(state.agents):
        #     return False

        for agent in state.identifier.actual:
            if not self.on_final(agent):
                return False

        return True


    def on_final(self, agent: Agent) -> bool:
        for i in self.goals:
            if i.x == agent.x and i.y == agent.y and i.color == agent.color:
                return True

        return False