from __future__ import annotations

from collections import defaultdict
from typing import Optional, Set, Dict, List
import gurobipy as gp
from gurobipy import GRB, Var, Constr
from pygraphviz import AGraph

from src.cbm.cbm_graph import GraphManager, NodeId, EdgeId, ConstraintContext, Time
from src.cbm.cbm_grid import CBMGrid
from src.cbm.cbm_low_level import CBMLowLevelSolver, CBMLowLevelAgentSolver
from src.cbm.ilp.cbm_ilp_gurobi import get_env
from src.ctnode import CTNode
from src.data.constraints import Constraint
from src.cbm.cbm_agent import CBMTeam
from src.cbm.cbm_paths import CBMAgentSolution
from src.data.vertex import Vertex
from src.debug.nf_drawer import draw_nf_graph
from src.grid import Grid
from src.util import range_incl


class ILPGraphManager(GraphManager):
    def __init__(self, grid: Grid, team: CBMTeam):
        super().__init__(grid, team, disappearing_agents=False)

        self.m = gp.Model(f"ilp_team_{self.team.id}", env=get_env())

        self.current_edge_id = 0

        self.current_node_supplies: Dict[NodeId, int] = dict()
        self.updated_node_supplies: Dict[NodeId, int] = dict()
        self.node_in_edges: Dict[NodeId, List[EdgeId]] = defaultdict(list)

        self.edge_tails: Dict[EdgeId, NodeId] = dict()
        self.edge_capacities: Dict[EdgeId, int] = dict()
        self.edge_vars: Dict[EdgeId, Var] = dict()

        self.flow_constraints: Dict[NodeId, Constr] = dict()
        self.edge_cap_constraints: Dict[EdgeId, Constr] = dict()

        self.indicator_vars: Dict[Vertex, Dict[Time, Var]] = defaultdict(dict)

    def create_node(self, node_i: NodeId):
        self.updated_node_supplies[node_i] = 0
        self.current_node_supplies[node_i] = 0

    def create_edge(self, s_node_i: NodeId, t_node_i: NodeId, capacity: int,
                    cost: int):
        edge_var: Var = self.m.addVar(obj=cost, name=f"{s_node_i}_{t_node_i}")
        edge_cap_constr: Constr = self.m.addConstr(
            edge_var <= capacity,
            f"edge_cap_{self.current_edge_id}_c{capacity}")

        self.edge_tails[self.current_edge_id] = t_node_i
        self.edge_capacities[self.current_edge_id] = capacity
        self.edge_vars[self.current_edge_id] = edge_var
        self.edge_cap_constraints[self.current_edge_id] = edge_cap_constr

        self.edge_ids[s_node_i][t_node_i] = self.current_edge_id
        self.node_in_edges[t_node_i].append(self.current_edge_id)
        self.node_out_edges[s_node_i].append(self.current_edge_id)

        self.updated_node_supplies.setdefault(
            s_node_i, self.current_node_supplies[s_node_i])
        self.updated_node_supplies.setdefault(
            t_node_i, self.current_node_supplies[t_node_i])

        self.current_edge_id += 1

    def update_node_supply(self, node_i: NodeId, new_supply: int):
        self.updated_node_supplies[node_i] = new_supply
        self.current_node_supplies[node_i] = new_supply

    def get_edge_capacity(self, edge_i: EdgeId) -> int:
        return self.edge_capacities[edge_i]

    def update_edge_capacity(self,
                             edge_i: EdgeId,
                             new_capacity: int,
                             temp: bool = True):
        super().update_edge_capacity(edge_i, new_capacity, temp)

        curr_constr = self.edge_cap_constraints[edge_i]
        self.m.remove(curr_constr)

        edge_var = self.edge_vars[edge_i]
        edge_cap_constr: Constr = self.m.addConstr(
            edge_var <= new_capacity, f"edge_cap_{edge_i}_c{new_capacity}")

        self.edge_capacities[edge_i] = new_capacity
        self.edge_cap_constraints[edge_i] = edge_cap_constr

    def get_edge_cost(self, edge_i: EdgeId) -> int:
        return self.edge_vars[edge_i].Obj

    def update_edge_cost(self,
                         edge_i: EdgeId,
                         new_cost: int,
                         temp: bool = True):
        super().update_edge_cost(edge_i, new_cost, temp)
        self.edge_vars[edge_i].Obj = new_cost

    def tail(self, edge_i: EdgeId) -> NodeId:
        return self.edge_tails[edge_i]


class CBMILPLowLevelAgentSolver(CBMLowLevelAgentSolver):
    def __init__(self, grid: Grid, team: CBMTeam, node: CTNode,
                 graph_manager: ILPGraphManager, constraints: Set[Constraint]):
        self.grid = grid
        self.team = team
        self.node = node

        self.graph_manager = graph_manager
        self.constraint_context = ConstraintContext(constraints)

    def solve(self, t_max: int,
              find_makespan: bool) -> Optional[CBMAgentSolution]:
        gm = self.graph_manager

        t_max = gm.get_future_max(t_max, self.constraint_context)
        t_min = 0 if gm.last_node_i == 0 else gm.graph_t_max

        gm.build_graph(t_max, find_makespan)
        gm.add_new_constraints(self.constraint_context)

        for goal in self.team.goals:
            for t in reversed(list(range_incl(t_min, t_max - 1))):
                indicator_var = gm.m.addVar(vtype=GRB.BINARY,
                                            name=f"indicator_{goal}_{t}")
                gm.indicator_vars[goal][t] = indicator_var

                out_node = gm.nodes_out_i[goal][t]
                in_node = gm.nodes_in_i[goal][t + 1]
                stay_edge_i = gm.edge_ids[out_node][in_node]
                stay_edge_var = gm.edge_vars[stay_edge_i]

                gm.m.addConstr((indicator_var == 1) >> (stay_edge_var >= 1),
                               name=f"indicator_constr_{goal}_{t}")

                if t != t_max - 1:
                    gm.m.addConstr((indicator_var == 1) >>
                                   (gm.indicator_vars[goal][t + 1] >= 1),
                                   name=f"indicator_constr2_{goal}{t}")

                if t == t_min and t > 0:
                    gm.m.addConstr((gm.indicator_vars[goal][t - 1] == 1) >>
                                   (indicator_var >= 1),
                                   name=f"indicator_constr2_{goal}{t}")

        for node_i in gm.updated_node_supplies.keys():
            if node_i in gm.flow_constraints:
                gm.m.remove(gm.flow_constraints[node_i])

        for node_i, supply in gm.updated_node_supplies.items():
            expr = (gp.quicksum(gm.edge_vars[e_i] for e_i in gm.node_in_edges[node_i]) + supply
                    == gp.quicksum(gm.edge_vars[e_i] for e_i in gm.node_out_edges[node_i]))  # yapf: disable

            flow_constr = gm.m.addConstr(expr, f"flow_{node_i}_s{supply}")
            gm.flow_constraints[node_i] = flow_constr

        gm.updated_node_supplies.clear()

        edge_sums = gp.quicksum(edge_var for edge_var in gm.edge_vars.values())
        indicator_sums = gp.quicksum(
            indicator_var
            for indicator_time_vars in gm.indicator_vars.values()
            for indicator_var in indicator_time_vars.values())
        gm.m.setObjective(edge_sums - indicator_sums, sense=GRB.MINIMIZE)

        def add_nodes_edges(graph: AGraph):
            model = gm.m
            constrs = model.getConstrs()
            for node_i, stats in gm.node_stats.items():
                flows = list(filter(lambda c: f"flow_{node_i}_" in c.ConstrName,constrs))  # yapf: disable
                assert len(flows) == 1
                graph.add_node(
                    node_i,
                    label=f"{stats.name} / {flows[0].ConstrName.split('_')[-1]}"
                )

            for edge_var in model.getVars():
                s_i, t_i = edge_var.VarName.split("_")
                edge_i = gm.edge_ids[int(s_i)][int(t_i)]
                graph.add_edge(
                    s_i,
                    t_i,
                    label=f"{int(edge_var.Obj)}/{gm.edge_capacities[edge_i]}")

        draw_nf_graph(add_nodes_edges)

        gm.m.optimize()

        if gm.m.status == GRB.OPTIMAL:
            return gm.assemble_flow_path(t_max,
                                         lambda e: gm.edge_vars[e].X > 0)

        return None


class CBMILPLowLevelSolver(CBMLowLevelSolver):
    def __init__(self, grid: CBMGrid, reset_teg: bool,
                 disappearing_agents: bool):
        super().__init__(grid, reset_teg, disappearing_agents)
        self._graph_managers: Dict[CBMTeam, ILPGraphManager] = {}

    def get_graph_manager(self, team: CBMTeam) -> ILPGraphManager:
        if team not in self._graph_managers:
            self._graph_managers[team] = ILPGraphManager(self.grid, team)
        return self._graph_managers[team]

    def get_agent_solver(
            self, node: CTNode, team: CBMTeam,
            team_constraints: Set[Constraint]) -> CBMLowLevelAgentSolver:
        return CBMILPLowLevelAgentSolver(self.grid, team, node,
                                         self.get_graph_manager(team),
                                         team_constraints)
