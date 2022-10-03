from __future__ import annotations


class Vertex:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

        self._str = f"({self.x}, {self.y})"
        self._hash = hash((self.x, self.y))

    def __str__(self) -> str:
        return self._str

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: Vertex) -> bool:
        # We only have one instance of each vertex
        return self is other
