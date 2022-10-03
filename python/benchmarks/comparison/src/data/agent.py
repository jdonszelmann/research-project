from __future__ import annotations


class Agent:
    def __init__(self, id: str) -> None:
        self.id = id
        self._hash = hash(id)

    def __str__(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: Agent) -> bool:
        # We only have one instance of each agent
        return self is other
