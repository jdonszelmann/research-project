from typing import Dict

from python.priority_queue import T
from python.priority_queue.simple import SimplePriorityQueue


class FastContainsPriorityQueue(SimplePriorityQueue):
    def __init__(self):
        super().__init__()
        self.cs: Dict[T, int] = {}

    def __contains__(self, item: T) -> bool:
        return item in self.cs

    def enqueue(self, item: T):
        super().enqueue(item)
        if item in self.cs:
            self.cs[item] += 1
        else:
            self.cs[item] = 1

    def dequeue(self) -> T:
        item = super().dequeue()

        if item in self.cs:
            if self.cs[item] > 1:
                self.cs[item] -= 1
            else:
                del self.cs[item]

        return item
