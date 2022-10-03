from __future__ import annotations

import csv
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Union, Optional, Tuple, List, TypeVar, Callable, Dict, Any

from src.env import CurrentSolver

# Map, runtime, solver
BasicCSVLayout = Tuple[str, str, str]

# Map, amount of agents, runtime, solver
JonathanCSVLayout = Tuple[str, str, str]

# Map, runtime, created nodes, created edges, solver
CreatedNodesEdgesCSVLayout = Tuple[str, str, str, str, str]  # yapf: disable

# Map, runtime, created nodes, created edges, conflicts, solver
ConflictsCSVLayout = Tuple[str, str, str, str, str, str]  # yapf: disable

CSVLayout = Union[BasicCSVLayout, JonathanCSVLayout, CreatedNodesEdgesCSVLayout, ConflictsCSVLayout]  # yapf: disable


class Field(Enum):
    RUNTIME = 0,
    NODES = 1,
    EDGES = 2,
    CONFLICTS = 3,
    AGENTS = 4,
    TEAMS = 5,
    MAP_NODES = 6,
    SOLVER = 7,
    PERCENTAGE_SOLVED = 8,


class BenchmarkResult:
    def __init__(self,
                 map_name: str,
                 amount_of_agents: int,
                 amount_of_teams: int,
                 runtime: Optional[float],
                 created_nodes: Optional[int],
                 created_edges: Optional[int],
                 conflicts: Optional[int],
                 solver: str,
                 is_averaged: bool = False,
                 orig_results: Optional[List[BenchmarkResult]] = None):
        self.map_name = map_name
        self.amount_of_agents = amount_of_agents
        self.amount_of_teams = amount_of_teams

        self.runtime = runtime
        self.created_nodes = created_nodes
        self.created_edges = created_edges
        self.conflicts = conflicts
        self.solver = solver

        self.is_averaged = is_averaged
        self.orig_results = orig_results

    def __str__(self) -> str:
        return f"{self.map_name} ({self.solver}, {self.runtime}) - N{self.created_nodes}, E{self.created_edges}, C{self.conflicts}"

    def has_solved(self) -> bool:
        return self.runtime is not None

    def get_field(self, field: Field) -> Any:
        if field == Field.RUNTIME:
            return self.runtime
        elif field == Field.NODES:
            return self.created_nodes
        elif field == Field.EDGES:
            return self.created_edges
        elif field == Field.CONFLICTS:
            print(self.conflicts)
            return self.conflicts
        elif field == Field.AGENTS:
            return self.amount_of_agents
        elif field == Field.TEAMS:
            return self.amount_of_teams
        elif field == Field.MAP_NODES:
            map_size = self.map_name.split("-")[1]
            width = int(map_size.split("x")[0])
            height = int(map_size.split("x")[1])
            return width * height
        elif field == Field.SOLVER:
            return self.solver

    @staticmethod
    def parse_csv_tuple(csv_tuple: CSVLayout) -> BenchmarkResult:
        map_name = str(csv_tuple[0])

        if len(csv_tuple) == 4:
            csv_tuple: JonathanCSVLayout = csv_tuple

            teams = int(map_name.split("_")[2].removesuffix("teams"))

            return BenchmarkResult(
                map_name=map_name,
                amount_of_agents=int(csv_tuple[1]),
                amount_of_teams=teams,
                runtime=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[2], float),
                created_nodes=None,
                created_edges=None,
                conflicts=None,
                solver=csv_tuple[3])

        agents, teams = BenchmarkResult.map_to_agents_teams(csv_tuple[0])
        if len(csv_tuple) == 3:
            csv_tuple: BasicCSVLayout = csv_tuple
            return BenchmarkResult(
                map_name=map_name,
                amount_of_agents=agents,
                amount_of_teams=teams,
                runtime=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[1], float),
                created_nodes=None,
                created_edges=None,
                conflicts=None,
                solver=str(BenchmarkResult.get_current_solver(csv_tuple[2])))
        elif len(csv_tuple) == 5:
            csv_tuple: CreatedNodesEdgesCSVLayout = csv_tuple
            return BenchmarkResult(
                map_name=map_name,
                amount_of_agents=agents,
                amount_of_teams=teams,
                runtime=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[1], float),
                created_nodes=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[2], int),
                created_edges=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[3], int),
                conflicts=None,
                solver=str(BenchmarkResult.get_current_solver(csv_tuple[4])))
        else:
            csv_tuple: ConflictsCSVLayout = csv_tuple
            return BenchmarkResult(
                map_name=map_name,
                amount_of_agents=agents,
                amount_of_teams=teams,
                runtime=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[1], float),
                created_nodes=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[2], int),
                created_edges=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[3], int),
                conflicts=BenchmarkResult.convert_if_not_empty(
                    csv_tuple[4], int),
                solver=str(BenchmarkResult.get_current_solver(csv_tuple[5])))

    @staticmethod
    def map_to_agents_teams(name: str) -> Tuple[int, int]:
        agents_teams = name.split("-")[2]
        agents = agents_teams.split("_")[0]
        teams = agents_teams.split("_")[1]
        return int(agents[1:]), int(teams[1:])

    @staticmethod
    def get_current_solver(name: str) -> CurrentSolver:
        return CurrentSolver[name.removeprefix("CurrentSolver.")]

    T = TypeVar("T")

    @staticmethod
    def convert_if_not_empty(data: str, f: Callable[[str], T]) -> Optional[T]:
        if len(data) > 0:
            return f(data)
        return None


def parse_set(data_dir: Path) -> List[BenchmarkResult]:
    all_results: List[BenchmarkResult] = []
    for file in data_dir.glob("./*.csv"):
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            all_results.extend(
                map(lambda t: BenchmarkResult.parse_csv_tuple(t), csv_reader))

    return average_results_and_fix_missing(all_results)


def average_results_and_fix_missing(
        results: List[BenchmarkResult]) -> List[BenchmarkResult]:
    map_solver_groups: Dict[(str, CurrentSolver),
                            List[BenchmarkResult]] = defaultdict(list)

    for result in results:
        map_solver_groups[(result.map_name, result.solver,
                           result.amount_of_agents,
                           result.amount_of_teams)].append(result)

    R = TypeVar("R")

    def compute_average(samples: List[BenchmarkResult],
                        f: Callable[[BenchmarkResult], R]) -> Optional[R]:
        total_value: R = 0
        amount_of_values = 0

        for sample in samples:
            value = f(sample)
            if value is not None:
                total_value += value
                amount_of_values += 1

        if amount_of_values == 0:
            return None
        return total_value / amount_of_values

    new_results: List[BenchmarkResult] = []
    for (map_name, solver, agents,
         teams), results in map_solver_groups.items():
        avg_runtime = compute_average(results, lambda r: r.runtime)
        avg_nodes = compute_average(results, lambda r: r.created_nodes)
        avg_edges = compute_average(results, lambda r: r.created_edges)
        avg_conflicts = compute_average(results, lambda r: r.conflicts)
        new_results.append(
            BenchmarkResult(map_name,
                            agents,
                            teams,
                            avg_runtime,
                            avg_nodes,
                            avg_edges,
                            avg_conflicts,
                            solver,
                            is_averaged=True,
                            orig_results=results))

    return new_results
