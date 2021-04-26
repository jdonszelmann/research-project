from typing import Any, Protocol


class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool: ...
