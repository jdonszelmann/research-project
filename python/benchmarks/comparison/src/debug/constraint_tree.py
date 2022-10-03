from __future__ import annotations

import pygraphviz
from collections import Set
from typing import Optional

from pathlib import Path

from src.data.constraints import Constraint


class ConstraintTree:
    def __init__(self, level: int, constraint: Optional[Constraint]):
        self.level = level
        self.constraint = constraint
        self.children: Set[ConstraintTree] = set()

    def add_constraint(self, constraint: Constraint) -> ConstraintTree:
        new_child = ConstraintTree(self.level + 1, constraint)
        self.children.add(new_child)
        return new_child


def draw_constraint_graph(ct: ConstraintTree):
    graph = pygraphviz.AGraph()
    node_id = 0

    def add_children(curr_ct: ConstraintTree, parent: Optional[str]):
        nonlocal node_id
        node_id += 1

        curr_node_id = str(node_id)
        graph.add_node(curr_node_id, label=str(curr_ct.constraint))

        if parent is not None:
            graph.add_edge(parent, curr_node_id)

        for child in curr_ct.children:
            add_children(child, curr_node_id)

    add_children(ct, None)

    graph.layout(prog="dot")
    vis_path = Path(__file__).parent / "ct_viz.svg"
    graph.draw(path=vis_path)
