from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from python.mstar.rewrite.config import Config
    from python.mstar.rewrite.goal import Goal
    from python.mstar.rewrite.grid import Grid
    from python.mstar.rewrite.optimal_path import OptimalPath
    from python.mstar.rewrite.statecache import StateCache
    from python.mstar.rewrite.heuristic import Heuristic
    from python.mstar.rewrite.state_cache_cache import StateCacheCache

from typing import Optional


class FindPathParams:
    """
    Object holding all arguments necessary for find_path.
    There are a lot so that's why they're grouped like this.
    """

    def __init__(self,
                 cfg: Config,
                 goal: Goal,

                 num_agents: int,

                 grid: Grid,
                 optimal_path: OptimalPath,
                 state_cache: StateCache,
                 heuristic: Heuristic,

                 state_cache_cache: Optional[StateCacheCache] = None  # only needed when cfg.recursive=True
                 ):

        self.cfg = cfg
        self.goal = goal
        self.num_agents = num_agents
        self.grid = grid
        self.optimal_path = optimal_path
        self.state_cache = state_cache
        self.heuristic = heuristic
        self.state_cache_cache = state_cache_cache
