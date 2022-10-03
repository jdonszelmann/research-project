import pickle

from pathlib import Path
from typing import Optional

import time

from src.ctnode import CTNode
from src.debug.constraint_tree import draw_constraint_graph
from src.env import get_env
from src.paths import FullSolution

intermediates_dir = Path(__file__).parent / "intermediates"


def high_level_debug_hook(root: CTNode, current_node: CTNode):
    if get_env().debug.ct_visualize:
        draw_constraint_graph(root.ct)

    if get_env().debug.intermediates.save:
        intermediates_dir.mkdir(parents=True, exist_ok=True)
        with open(intermediates_dir / f"intermediate_{time.time()}",
                  "wb") as file:
            pickle.dump(current_node.full_solution, file)


def load_intermediate_solution() -> Optional[FullSolution]:
    if len(get_env().debug.intermediates.load_path) > 0:
        with open(intermediates_dir / get_env().debug.intermediates.load_path,
                  "rb") as file:
            return pickle.load(file)
