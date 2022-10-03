import logging
from collections import Callable
from pathlib import Path

import time
from pygraphviz import AGraph

from src.env import get_env


def draw_nf_graph(add_nodes_edges: Callable[[AGraph]]):
    if not get_env().debug.nf_visualize:
        return

    graph = AGraph(directed=True)

    logging.info("DRAWING NF GRAPH...")
    add_nodes_edges(graph)

    graph.layout(prog="fdp")

    vis_dir = Path(__file__).parent / "nf_viz"
    vis_dir.mkdir(parents=True, exist_ok=True)
    graph.draw(path=vis_dir / f"nf_viz_{time.time()}.svg")
