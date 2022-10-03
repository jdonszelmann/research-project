from src.data.agent import Agent
from src.data.vertex import Vertex


class AstarAgent(Agent):
    def __init__(self, id: str, start: Vertex, goal: Vertex) -> None:
        super().__init__(id)
        self.start = start
        self.goal = goal
