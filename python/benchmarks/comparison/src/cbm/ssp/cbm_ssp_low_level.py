from __future__ import annotations

from typing import Optional, Set, Dict, Tuple

from ortools.graph import pywrapgraph
from pygraphviz import AGraph

from src.cbm.cbm_graph import GraphManager, NodeId, ConstraintContext, EdgeId, Time
from src.cbm.cbm_grid import CBMGrid
from src.cbm.cbm_low_level import CBMLowLevelSolver, CBMLowLevelAgentSolver
from src.ctnode import CTNode
from src.cbm.cbm_agent import CBMTeam
from src.cbm.cbm_paths import CBMAgentSolution, CBMMakespanFullSolution
from src.data.constraints import Constraint
from src.debug.nf_drawer import draw_nf_graph
from src.grid import Grid


class SSPGraphManager(GraphManager):
    def __init__(self, grid: Grid, team: CBMTeam, disappearing_agents: bool):
        super().__init__(grid, team, disappearing_agents)

        self.cost_flow = pywrapgraph.SimpleMinCostFlow()

        self.starts_i: Set[Tuple[CBMTeam, NodeId]] = set()

    def create_edge(self, s_node_i: NodeId, t_node_i: NodeId, capacity: int,
                    cost: int):
        super().create_edge(s_node_i, t_node_i, capacity, cost)

        edge_id = self.cost_flow.AddArcWithCapacityAndUnitCost(
            s_node_i, t_node_i, capacity, cost)
        self.edge_ids[s_node_i][t_node_i] = edge_id
        self.node_out_edges[s_node_i].append(edge_id)

    def update_node_supply(self, node_i: NodeId, new_supply: int):
        self.cost_flow.SetNodeSupply(node_i, new_supply)

    def get_edge_capacity(self, edge_i: EdgeId) -> int:
        return self.cost_flow.Capacity(edge_i)

    def update_edge_capacity(self,
                             edge_i: EdgeId,
                             new_capacity: int,
                             temp: bool = True):
        super().update_edge_capacity(edge_i, new_capacity, temp)
        self.cost_flow.SetArcCapacity(edge_i, new_capacity)

    def get_edge_cost(self, edge_i: EdgeId) -> int:
        return self.cost_flow.UnitCost(edge_i)

    def update_edge_cost(self,
                         edge_i: EdgeId,
                         new_cost: int,
                         temp: bool = True):
        super().update_edge_cost(edge_i, new_cost, temp)
        self.cost_flow.SetArcCost(edge_i, new_cost)

    def tail(self, edge_i: EdgeId) -> NodeId:
        # Or-tools switches around tail & head for some reason
        return self.cost_flow.Head(edge_i)

    def get_intended_edge_cost(self, is_goal: bool, t: Time, t_max: Time,
                               find_makespan: bool) -> int:

        if find_makespan:
            return 0
        elif self.disappearing_agents:
            return 1
        else:
            if is_goal:
                return t_max - t - 1
            else:
                return int(len(self.team.goals) * t_max * (t_max - 1) / 2)


class CBMSSPLowLevelAgentSolver(CBMLowLevelAgentSolver):
    def __init__(self, grid: Grid, team: CBMTeam, node: CTNode,
                 graph_manager: SSPGraphManager, constraints: Set[Constraint],
                 reset_teg: bool, disappearing_agents: bool):
        self.grid = grid
        self.team = team
        self.node = node

        self.reset_teg = reset_teg
        self.disappearing_agents = disappearing_agents

        self.graph_manager = graph_manager
        self.constraint_context = ConstraintContext(constraints)

    def apply_cbm_reductions(self):
        assert self.node.full_solution is not None
        assert isinstance(self.node.full_solution, CBMMakespanFullSolution)

        gm = self.graph_manager

        # 1: set weights of edges to 0 initially
        # Is already done by CBM_graph

        # 2: increment the weight of each (v_t_in, v_t_out) in other team's paths
        for team in self.grid.agents:
            if team == self.team:
                continue

            for agent, path in self.node.full_solution[team]:
                for t, v in enumerate(path):
                    # We can't prevent it from being at the source
                    if t not in gm.nodes_in_i[v]:
                        continue

                    node_in_i = gm.nodes_in_i[v][t]
                    node_out_i = gm.nodes_out_i[v][t]

                    e_i = gm.edge_ids[node_in_i][node_out_i]
                    gm.update_edge_cost(e_i, gm.get_edge_cost(e_i) + 1)

        # 3: increment the weight of each (v_t_in, w) in other team's paths
        for team in self.grid.agents:
            if team == self.team:
                continue

            for agent, path in self.node.full_solution[team]:
                for t, (u, v) in enumerate(zip(path, path[1:])):
                    if u is v or t not in gm.nodes_out_i[v]:
                        continue

                    node_out_i = gm.nodes_out_i[v][t]
                    w_id = gm.w_i[u][v][t] if t in gm.w_i[u][v] else gm.w_i[v][u][t]  # yapf: disable

                    e_i = gm.edge_ids[node_out_i][w_id]
                    gm.update_edge_cost(e_i, gm.get_edge_cost(e_i) + 1)

    def solve(self, t_max: int,
              find_makespan: bool) -> Optional[CBMAgentSolution]:
        if self.reset_teg:
            self.graph_manager = SSPGraphManager(self.grid, self.team,
                                                 self.disappearing_agents)
        else:
            self.graph_manager.reset_temp_state()

        t_max = self.graph_manager.get_future_max(t_max,
                                                  self.constraint_context)

        self.graph_manager.build_graph(t_max, find_makespan)

        if self.node.full_solution is not None and find_makespan:
            self.apply_cbm_reductions()
        self.graph_manager.add_new_constraints(self.constraint_context)

        def add_nodes_edges(graph: AGraph):
            flow = self.graph_manager.cost_flow
            for node_i in range(flow.NumNodes()):
                graph.add_node(
                    node_i,
                    label=
                    f"{self.graph_manager.node_stats[node_i].name} / s{self.graph_manager.cost_flow.Supply(node_i)}"
                )

            for edge_i in range(flow.NumArcs()):
                graph.add_edge(
                    flow.Tail(edge_i),
                    flow.Head(edge_i),
                    label=f"{flow.UnitCost(edge_i)}/{flow.Capacity(edge_i)}")

        draw_nf_graph(add_nodes_edges)

        if self.graph_manager.cost_flow.Solve() == self.graph_manager.cost_flow.OPTIMAL:  # yapf: disable
            return self.graph_manager.assemble_flow_path(
                t_max,
                lambda edge_i: self.graph_manager.cost_flow.Flow(edge_i) > 0)

        return None


class CBMSSPLowLevelSolver(CBMLowLevelSolver):
    def __init__(self, grid: CBMGrid, reset_teg: bool,
                 disappearing_agents: bool):
        super().__init__(grid, reset_teg, disappearing_agents)
        self._graph_managers: Dict[CBMTeam, SSPGraphManager] = {}

    def get_graph_manager(self, team: CBMTeam) -> SSPGraphManager:
        if team not in self._graph_managers:
            self._graph_managers[team] = SSPGraphManager(
                self.grid, team, self.disappearing_agents)
        return self._graph_managers[team]

    def get_agent_solver(
            self, node: CTNode, team: CBMTeam,
            team_constraints: Set[Constraint]) -> CBMLowLevelAgentSolver:
        return CBMSSPLowLevelAgentSolver(self.grid, team, node,
                                         self.get_graph_manager(team),
                                         team_constraints, self.reset_teg,
                                         self.disappearing_agents)
