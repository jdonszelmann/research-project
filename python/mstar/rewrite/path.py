from python.mstar.state import State


class Path:
    def __init__(self, path: list[State]):
        self.path = path

    @property
    def cost(self) -> int:
        return self.path[-1].cost
