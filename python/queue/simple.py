import heapq
from typing import List

from python.queue import PriorityQueue, T, UniqueIdentifier


class SimplePriorityQueue(PriorityQueue):
    def __init__(self):
        self.pq: List[T] = []

    def __contains__(self, item: UniqueIdentifier) -> bool:
        for i in self.pq:
            if i.identifier == item.identifier:
                return True
        return False

    def enqueue(self, item: T):
        heapq.heappush(self.pq, item)

    def dequeue(self) -> T:
        return heapq.heappop(self.pq)

    def empty(self) -> bool:
        return len(self.pq) == 0
