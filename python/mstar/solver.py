import copy
from itertools import product
from typing import Type, List, Iterable, Set, Callable

from mapfmclient import MarkedLocation

from python.agent import Agent
from python.astar.no_solution import NoSolutionError
from python.coord import Coord
from python.mstar.problem import MStarProblem
from python.mstar.state import MStarState
from python.priority_queue import PriorityQueue


class MStarSolver(MStarProblem):
    def __init__(self, starts: List[MarkedLocation], ends: List[MarkedLocation], grid: List[List[int]], width: int,
                 height: int, queue_type: Type[PriorityQueue]):
        self.starts = starts
        self.ends = ends
        self.grid = grid
        self.width = width
        self.height = height

        self.pq_type = queue_type

        self.start_state = MStarState.from_starts(starts, self.heuristic)

    def wall_at(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 1

    def on_final(self, agent: Agent) -> bool:
        for i in self.ends:
            if i.x == agent.x and i.y == agent.y and i.color == agent.color:
                return True

        return False

    @staticmethod
    def collisions(old_state: List[Agent], new_state: List[Agent]) -> Set[Agent]:
        assert len(old_state) == len(new_state)
        res = set()

        for a1 in range(len(old_state)):
            for a2 in range(min(a1, len(new_state))):
                if new_state[a1] == new_state[a2]:
                    res.add(new_state[a1])
                    res.add(new_state[a2])

                elif old_state[a1] == new_state[a2] and new_state[a1] == old_state[a2]:
                    # TODO: is this right?
                    res.add(old_state[a1])
                    res.add(new_state[a2])

        return res

    def initial_state(self) -> MStarState:
        return self.start_state

    def final_state(self, state: MStarState) -> bool:
        # implied by constraints on move
        # if self.has_double(state.agents):
        #     return False

        for agent in state.agents:
            if not self.on_final(agent):
                return False

        return True

    def heuristic(self, state: MStarState) -> int:
        res = 0
        for index, agent in enumerate(state.agents):
            best = None
            for i in self.ends:
                if agent.color == i.color:
                    dist = abs(i.x - agent.x) + abs(i.y - agent.y)
                    if best is None or best < dist:
                        best = dist
            res += best
        return res

    # all the directions you can move in
    directions = [Coord(0, -1), Coord(0, 1), Coord(1, 0), Coord(-1, 0)]

    def neighbours(self, parent: MStarState, in_queue: Callable[[MStarState], bool]) -> Iterable[MStarState]:
        all_agent_possibilities = []
        for agent in parent:
            neighbours = []
            for i in self.directions:
                p = i + agent.location

                if not p.out_of_bounds(self.width, self.height) and not self.wall_at(p.x, p.y):
                    neighbours.append((p, 0, agent.accumulated_cost + 1))

            if self.on_final(agent):
                neighbours.append((agent.location, agent.accumulated_cost + 1, 0))
            else:
                neighbours.append((agent.location, 0, 1))

            all_agent_possibilities.append(neighbours)

        possible_next_states = product(*all_agent_possibilities)

        next_states = []
        for state in possible_next_states:

            cost = 0
            next_agents = []
            for agent, (coord, acc, c) in zip(parent.agents, state):
                next_agents.append(Agent(coord, agent.color, acc))
                cost += c

            next_state = MStarState(next_agents, cost, 0, parent)
            next_state.set_heuristic(self.heuristic)

            collisions = self.collisions(parent.agents, next_state.agents)
            next_state.back_set.add(parent)
            next_state.collision_set = next_state.collision_set.union(collisions)

            next_states.extend(self.backprop(parent, next_state.collision_set, in_queue))

            if len(collisions) == 0 and parent.cost + cost < next_state.cost:
                next_states.append(next_state)

        return next_states

    def backprop(self,
                 parent: MStarState,
                 new_collision_set: Set[Agent],
                 in_queue: Callable[[MStarState], bool]
                 ) -> Iterable[MStarState]:

        res = []
        if not new_collision_set.issubset(parent.collision_set):
            new_parent = parent.copy()
            new_parent.collision_set = new_parent.collision_set.union(new_collision_set)
            # TODO: is in_queue necessary?
            # NOTE: by using in_queue, we know that this item is not in the queue anymore,
            # and we must have the only reference to it. It's therefore safe
            # to mutate the heuristic here without copying the parent
            if not in_queue(parent):
                res.append(new_parent)

            for i in parent.back_set:
                self.backprop(i, parent.collision_set, in_queue)

        return res

    def search(self) -> List[MStarState]:
        initial_state = self.initial_state()

        pq = self.pq_type()

        pq.enqueue(initial_state)

        while not pq.empty():
            curr = pq.dequeue()

            if self.final_state(curr):
                print(curr.cost)
                return curr.backtrack()

            neighbours = self.neighbours(curr, pq.__contains__)

            for n in neighbours:
                pq.enqueue(n)

        raise NoSolutionError