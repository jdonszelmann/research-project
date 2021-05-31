from __future__ import annotations
from enum import Enum

import resource

class MatchingStrategy(Enum):
    Prematch = 0,
    PruningPrematch = 1,
    SortedPruningPrematch = 2,
    Inmatch = 3,


Byte = 1
KiloByte = Byte * 1024
MegaByte = KiloByte * 1024
GigaByte = MegaByte * 1024

class Config:
    def __init__(
            self,
            operator_decomposition: bool = False,
            precompute_paths: bool = False,
            precompute_heuristic: bool = False,
            collision_avoidance_table: bool = False,
            recursive: bool = False,
            matching_strategy: MatchingStrategy = MatchingStrategy.Prematch,
            max_memory_usage: int = 3 * GigaByte,
            debug: bool = False
    ):
        self.operator_decomposition = operator_decomposition
        self.precompute_paths = precompute_paths
        self.precompute_heuristic = precompute_heuristic
        self.collision_avoidance_table = collision_avoidance_table
        self.recursive = recursive
        self.matching_strategy = matching_strategy

        self.max_memory_usage = max_memory_usage
        self.debug = debug

    @property
    def prematch(self) -> bool:
        return (
                self.matching_strategy == MatchingStrategy.Prematch or
                self.matching_strategy == MatchingStrategy.PruningPrematch or
                self.matching_strategy == MatchingStrategy.SortedPruningPrematch
        )

    @property
    def pruning_prematch(self) -> bool:
        return (
                self.matching_strategy == MatchingStrategy.PruningPrematch or
                self.matching_strategy == MatchingStrategy.SortedPruningPrematch
        )

    @property
    def inmatch(self) -> bool:
        return self.matching_strategy == MatchingStrategy.Inmatch

    def memory_usage_ok(self) -> bool:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        if self.debug:
            print(f"{usage / MegaByte} megabytes used out of {self.max_memory_usage / MegaByte}")

        return usage < self.max_memory_usage
