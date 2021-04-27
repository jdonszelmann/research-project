import heapq
from typing import List

from python.priority_queue import PriorityQueue, T, UniqueIdentifier


class SimplePriorityQueue(PriorityQueue):
    def __init__(self):
        self.pq: List[T] = []

    def __contains__(self, item: T) -> bool:
        return item in self.pq

    def enqueue(self, item: T):
        heapq.heappush(self.pq, item)

    def dequeue(self) -> T:
        return heapq.heappop(self.pq)

    def empty(self) -> bool:
        return len(self.pq) == 0
