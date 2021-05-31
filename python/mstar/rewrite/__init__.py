from typing import Optional

from mapfmclient import Problem, MarkedLocation
from tqdm import tqdm

from python.mstar.rewrite.config import Config, MatchingStrategy
from python.mstar.rewrite.grid import Grid
from python.mstar.rewrite.heuristic import Heuristic
from python.mstar.rewrite.identifier import Identifier
from python.mstar.rewrite.find_path import find_path
from python.mstar.rewrite.optimal_path import OptimalPath
from python.mstar.rewrite.path import Path
from python.mstar.rewrite.path_cache import PathCache
from python.mstar.rewrite.state import State
from python.mstar.rewrite.statecache import StateCache
from python.mstar.rewrite.goal import StateGoal, AllAgentGoal
from python.mstar.rewrite.matchings import matchings


class MatchingWithHeuristic:
    def __init__(self, cfg: Config, matching: list[MarkedLocation], start_state: State, state_cache: StateCache, path_cache: PathCache):
        self.matching = matching


        self.goal_identifier = Identifier.from_marked_locations(matching)
        self.goal_state = state_cache.get(self.goal_identifier)
        self.goal = StateGoal(self.goal_state)

        self.optimal_path = OptimalPath(
            cfg,
            path_cache,

            goal_state=self.goal_state,
        )


        self.heuristic = Heuristic(cfg, self.optimal_path)

        if cfg.pruning_prematch:
            self.heuristic_value = self.heuristic.heuristic(start_state)


def mstar(cfg: Config, problem: Problem) -> Optional[Path]:
    grid = Grid(problem.grid)

    state_cache = StateCache(cfg, State)
    path_cache = PathCache(
        cfg,
        grid,
        problem.goals
    )

    start_identifier = Identifier.from_marked_locations(problem.starts)
    start_state = state_cache.get(start_identifier)

    num_agents = len(problem.starts)

    if cfg.prematch:

        best_path: Optional[Path] = None

        all_matchings: list[MatchingWithHeuristic] = [
            MatchingWithHeuristic(cfg, i, start_state, state_cache, path_cache)
            for i in matchings(problem.starts, problem.goals)
        ]

        if cfg.matching_strategy == MatchingStrategy.SortedPruningPrematch:
            all_matchings.sort(key=lambda i: i.heuristic_value)


        for matching in tqdm(all_matchings):
            if cfg.pruning_prematch:
                # if cfg.debug:
                if best_path is not None and matching.heuristic_value >= best_path.cost:
                    tqdm.write("pruned")
                    continue

            state_cache.reset()

            found_path = find_path(
                cfg,
                start_state, matching.goal,

                num_agents=num_agents,

                grid=grid,
                optimal_path=matching.optimal_path,
                state_cache=state_cache,
                heuristic=matching.heuristic,
            )

            if found_path is not None:
                if best_path is None or found_path.cost < best_path.cost:
                    best_path = found_path
            else:
                tqdm.write("no solution found")


        return best_path

    else:
        goal = AllAgentGoal(problem.goals)
        optimal_path = OptimalPath(
            cfg,
            path_cache,
        )

        heuristic = Heuristic(cfg, optimal_path)

        return find_path(
            cfg,
            start_state, goal,

            num_agents=num_agents,

            grid=grid,
            optimal_path=optimal_path,
            state_cache=state_cache,
            heuristic=heuristic,
        )
