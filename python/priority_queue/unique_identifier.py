from typing import Protocol


class UniqueIdentifier(Protocol):
    @property
    def identifier(self) -> int:
        return id(self)

