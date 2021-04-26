from typing import Set

from python.queue import T
from python.queue.simple import SimplePriorityQueue


class FastContainsPriorityQueue(SimplePriorityQueue):
    def __init__(self):
        super().__init__()
        self.cs: Set[int] = set()

    def __contains__(self, item: T) -> bool:
        return item in self.cs

    def enqueue(self, item: T):
        super().enqueue(item)
        self.cs.add(item.identifier)

    def dequeue(self) -> T:
        item = super().dequeue()
        self.cs.remove(item.identifier)
        return item
