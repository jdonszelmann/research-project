from __future__ import annotations

import logging
from collections import defaultdict
from typing import Optional, Dict, Set, List, Callable, Tuple

from src.cbm.cbm_agent import CBMTeam
from src.cbm.cbm_paths import CBMAgentSolution
from src.data.constraints import Constraint, VertexConstraint, EdgeConstraint
from src.data.vertex import Vertex
from src.env import get_env
from src.grid import Grid
from src.util import range_incl

NodeId = int
EdgeId = int
Time = int


class NodeStats:
    def __init__(self, v: Optional[Vertex], t: Time, name: Optional[str]):
        self.v = v
        self.t = t
        self.name = name


class ConstraintContext:
    def __init__(self, constraints: Set[Constraint]):
        self.v_constraints: Dict[Vertex, Dict[Time, VertexConstraint]] = defaultdict(dict)  # yapf: disable
        self.e_constraints: Dict[(Vertex, Vertex), Dict[Time, EdgeConstraint]] = defaultdict(dict)  # yapf: disable

        for c in constraints:
            if isinstance(c, VertexConstraint):
                self.v_constraints[c.v][c.t] = c
            elif isinstance(c, EdgeConstraint):
                self.e_constraints[c.e][c.t] = c


class GraphManager:
    created_nodes = 0
    created_edges = 0

    def __init__(self, grid: Grid, team: CBMTeam,
                 disappearing_agents: bool) -> None:
        self.grid = grid
        self.team = team

        self.has_updated_for_sic = False

        self.starts_i: Set[Tuple[CBMTeam, NodeId]] = set()

        # Node data
        self.nodes_out_i: Dict[Vertex, Dict[Time, NodeId]] = defaultdict(dict)
        self.nodes_in_i: Dict[Vertex, Dict[Time, NodeId]] = defaultdict(dict)
        self.w_i: Dict[Vertex, Dict[Vertex, Dict[Time, NodeId]]] = defaultdict(
            lambda: defaultdict(dict))
        self.w_acc_i: Dict[Vertex, Dict[Vertex, Dict[
            Time, NodeId]]] = defaultdict(lambda: defaultdict(dict))
        self.node_stats: Dict[NodeId, NodeStats] = dict()

        # Edge data
        self.edge_ids: Dict[NodeId, Dict[NodeId, EdgeId]] = defaultdict(dict)
        self.node_out_edges: Dict[NodeId, List[EdgeId]] = defaultdict(list)

        # Disappearing agent data
        self.disappear_goal_ids: Dict[Vertex, Dict[Time,
                                                   NodeId]] = defaultdict(dict)
        self.disappear_goal_main_id: NodeId = None

        # Previous run states
        self.last_node_i = 0
        self.graph_t_max = -1
        self.prev_t_max = -1

        self.prev_edge_cost: Dict[EdgeId, int] = dict()
        self.prev_edge_capacity: Dict[EdgeId, int] = dict()

        self.disappearing_agents = disappearing_agents

    def create_node(self, node_i: NodeId):
        GraphManager.created_nodes += 1

    def create_edge(self, s_node_i: NodeId, t_node_i: NodeId, capacity: int,
                    cost: int):
        GraphManager.created_edges += 1

    def update_node_supply(self, node_i: NodeId, new_supply: int):
        raise NotImplementedError("Override this one")

    def get_edge_capacity(self, edge_i: EdgeId) -> int:
        raise NotImplementedError("Override this one")

    def update_edge_capacity(self,
                             edge_i: EdgeId,
                             new_capacity: int,
                             temp: bool = True):
        if temp:
            self.prev_edge_capacity[edge_i] = self.get_edge_capacity(edge_i)

    def get_edge_cost(self, edge_i: EdgeId) -> int:
        raise NotImplementedError("Override this one")

    def update_edge_cost(self,
                         edge_i: EdgeId,
                         new_cost: int,
                         temp: bool = True):
        if temp:
            self.prev_edge_cost[edge_i] = self.get_edge_cost(edge_i)

    def tail(self, edge_i: EdgeId) -> NodeId:
        raise NotImplementedError("Override this one")

    def get_intended_edge_cost(self, is_goal: bool, t: Time, t_max: Time,
                               find_makespan: bool) -> int:
        return 1

    def reset_temp_state(self):
        for edge, orig_cost in self.prev_edge_cost.items():
            self.update_edge_cost(edge, orig_cost, temp=False)
        self.prev_edge_cost.clear()

        for edge, orig_capacity in self.prev_edge_capacity.items():
            self.update_edge_capacity(edge, orig_capacity, False)
        self.prev_edge_capacity.clear()

    def get_future_max(self, t_max: Time,
                       constraint_context: ConstraintContext) -> Time:
        for goal in self.team.goals:
            time_constraints = list(
                filter(lambda c: c.t >= t_max,
                       constraint_context.v_constraints[goal].values()))

            if len(time_constraints) > 0:
                t_max = max(map(lambda c: c.t, time_constraints))

        return t_max

    def add_new_constraints(self, constraint_context: ConstraintContext):
        for v, ts in constraint_context.v_constraints.items():
            for t, vc in ts.items():
                source = self.nodes_in_i[v][t]
                target = self.nodes_out_i[v][t]
                self.update_edge_capacity(self.edge_ids[source][target],
                                          new_capacity=0)

        for (u, v), ts in constraint_context.e_constraints.items():
            for t, ec in ts.items():
                if t >= self.graph_t_max:
                    continue

                (w_u, w_v) = (u, v) if t in self.w_i[u][v] else (v, u)

                source = self.nodes_out_i[u][t - 1]
                w_i = self.w_i[w_u][w_v][t - 1]
                self.update_edge_capacity(self.edge_ids[source][w_i],
                                          new_capacity=0)

                w_acc_i = self.w_acc_i[w_u][w_v][t - 1]
                target = self.nodes_in_i[v][t]
                self.update_edge_capacity(self.edge_ids[w_acc_i][target],
                                          new_capacity=0)

    def build_graph(self, t_max: Time, find_makespan: bool):
        """
        :param t_max: the new t-max
        :param prev_t_max: the previous max time-step
        :param find_makespan: are we finding the makespan or not?
        """

        if not find_makespan:
            if self.has_updated_for_sic:
                return
            else:
                logging.info("Searching for SIC now!")
                self.has_updated_for_sic = True

        enable_viz = get_env().debug.nf_visualize

        is_initial_run = self.last_node_i == 0
        t_min = self.graph_t_max + 1

        # Reset the node supply to 0 for the last run
        if is_initial_run and self.disappearing_agents:
            main_id = self.last_node_i
            self.create_node(main_id)

            self.disappear_goal_main_id = main_id
            self.node_stats[main_id] = NodeStats(
                None, -1, f"GOAL_MAIN" if enable_viz else None)

            self.update_node_supply(main_id, -len(self.team.goals))

            self.last_node_i += 1
        elif not is_initial_run:
            if t_max > self.graph_t_max:
                logging.info(
                    f"Extending graph for team from {self.graph_t_max} {self.team.id} to t{t_max}"
                )

            for goal in self.team.goals:
                self.update_node_supply(
                    self.nodes_out_i[goal][self.prev_t_max], 0)

            if t_max < self.graph_t_max:
                for ts in self.nodes_out_i.values():
                    for e_i in self.node_out_edges[ts[t_max]]:
                        self.update_edge_capacity(e_i, new_capacity=0)

        # Add in and out nodes for each vertex and their corresponding edges
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                v = self.grid.get_vertex(x, y)
                if v is None:
                    continue

                for t in range_incl(t_min, t_max):
                    # Vertex v at the end of time t
                    out_i = self.last_node_i
                    self.create_node(out_i)

                    self.nodes_out_i[v][t] = out_i
                    self.node_stats[out_i] = NodeStats(
                        v, t, f"({x}, {y})_out_t{t}" if enable_viz else None)

                    self.last_node_i += 1

                for t in range_incl(1 if is_initial_run else t_min, t_max):
                    # Vertex v at the start of time t
                    in_i = self.last_node_i
                    self.create_node(in_i)

                    self.nodes_in_i[v][t] = in_i
                    self.node_stats[in_i] = NodeStats(
                        v, t, f"({x}, {y})_in_t{t}" if enable_viz else None)

                    self.last_node_i += 1

                for t in range_incl(0, t_max - 1):
                    # Agent staying at v between t and t + 1
                    cost = self.get_intended_edge_cost(v in self.team.goals, t,
                                                       t_max, find_makespan)

                    node_out = self.nodes_out_i[v][t]
                    node_in = self.nodes_in_i[v][t + 1]

                    if t >= self.graph_t_max:
                        self.create_edge(node_out,
                                         node_in,
                                         capacity=1,
                                         cost=cost)
                    else:
                        edge_i = self.edge_ids[node_out][node_in]
                        self.update_edge_cost(edge_i, cost, temp=False)

                for t in range_incl(1 if is_initial_run else t_min, t_max):
                    # Prevents vertex collisions among all agents since only one agent can occupy a vertex
                    self.create_edge(self.nodes_in_i[v][t],
                                     self.nodes_out_i[v][t],
                                     capacity=1,
                                     cost=0)

        # Populate the start/end nodes with supply/demand
        for agent in self.team.agents:
            self.update_node_supply(self.nodes_out_i[agent.start][0], 1)

        if self.disappearing_agents:
            for t in range_incl(t_min, t_max):
                for goal in self.team.goals:
                    # Create goal node
                    goal_i = self.last_node_i
                    self.create_node(goal_i)

                    self.disappear_goal_ids[goal][t] = goal_i
                    self.node_stats[goal_i] = NodeStats(
                        None, t, f"GOAL_{goal}_t{t}" if enable_viz else None)

                    self.last_node_i += 1

                    # Create to goal edge
                    self.create_edge(self.nodes_out_i[goal][t], goal_i, 1, 0)
                    self.create_edge(goal_i, self.disappear_goal_main_id, 1, 0)
        else:
            for goal in self.team.goals:
                self.update_node_supply(self.nodes_out_i[goal][t_max], -1)

        # Add the gadget and the corresponding edges
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                u = self.grid.get_vertex(x, y)
                if u is None:
                    continue

                for t in range_incl(0, t_max - 1):
                    for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                        v = self.grid.get_vertex(x + dx, y + dy)
                        if v is None:
                            continue

                        is_u_v = t in self.w_i[u][v]
                        is_v_u = t in self.w_i[v][u]

                        cost = self.get_intended_edge_cost(
                            False, t, t_max, find_makespan)
                        if t < self.graph_t_max and is_u_v:
                            w_i = self.w_i[u][v][t]
                            w_acc_i = self.w_acc_i[u][v][t]
                            edge_i = self.edge_ids[w_i][w_acc_i]
                            self.update_edge_cost(edge_i, cost, temp=False)
                        elif not is_u_v and not is_v_u:
                            # Create w node
                            w_i = self.last_node_i
                            self.create_node(w_i)

                            self.w_i[u][v][t] = w_i
                            self.node_stats[w_i] = NodeStats(
                                None, t,
                                f"w_{u}_{v}_t{t}" if enable_viz else None)

                            self.last_node_i += 1

                            # Create w' node
                            w_acc_i = self.last_node_i
                            self.create_node(w_acc_i)

                            self.w_acc_i[u][v][t] = w_acc_i
                            self.node_stats[w_acc_i] = NodeStats(
                                None, t,
                                f"w'_{u}_{v}_t{t}" if enable_viz else None)

                            self.last_node_i += 1

                            # Create gadget edges
                            self.create_edge(self.nodes_out_i[u][t],
                                             w_i,
                                             capacity=1,
                                             cost=0)
                            self.create_edge(self.nodes_out_i[v][t],
                                             w_i,
                                             capacity=1,
                                             cost=0)

                            self.create_edge(w_i,
                                             w_acc_i,
                                             capacity=1,
                                             cost=cost)

                            self.create_edge(w_acc_i,
                                             self.nodes_in_i[u][t + 1],
                                             capacity=1,
                                             cost=0)

                            self.create_edge(w_acc_i,
                                             self.nodes_in_i[v][t + 1],
                                             capacity=1,
                                             cost=0)

        self.prev_t_max = t_max
        self.graph_t_max = max(self.graph_t_max, t_max)

    def assemble_flow_path(
            self, t_max: int,
            has_flow: Callable[[EdgeId], bool]) -> Optional[CBMAgentSolution]:
        agent_solution = CBMAgentSolution()

        if len(self.starts_i) == 0:
            self.starts_i = set(
                map(lambda a: (a, self.nodes_out_i[a.start][0]),
                    self.team.agents))

        goals_i = set(
            map(lambda g: self.disappear_goal_main_id, self.team.goals))

        for a, start_i in self.starts_i:
            curr_node_i = start_i

            path: List[Vertex] = []
            path_set: Dict[Vertex, Set[int]] = defaultdict(set)

            while True:
                node_stats = self.node_stats[curr_node_i]
                if node_stats.v is not None and node_stats.t not in path_set[node_stats.v]:  # yapf: disable
                    path_set[node_stats.v].add(node_stats.t)
                    path.append(node_stats.v)

                if curr_node_i in goals_i:
                    agent_solution.append((a, path))
                    break

                has_next_edge = False
                for edge_i in self.node_out_edges[curr_node_i]:
                    if has_flow(edge_i):
                        curr_node_i = self.tail(edge_i)
                        has_next_edge = True
                        break

                if not has_next_edge:
                    return None

        return agent_solution
