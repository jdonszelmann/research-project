import unittest

from python.mstar.rewrite.collisionset import RecursiveCollisionSet


class TestRecursiveCollisionSet(unittest.TestCase):
    def tests_from_colliding_indices(self):
        s = RecursiveCollisionSet.from_colliding_indices([
            (1, 2),
            (2, 3),
            (4, 5),
        ])

        one = frozenset([1, 2, 3])
        two = frozenset([4, 5])

        self.assertEqual(len(s.set), 2)
        self.assertTrue(one in s.set)
        self.assertTrue(two in s.set)


    def test_subset(self):
        for a, b, ans in [
            ([], [[1, 2, 3]], True),
            ([[]], [[1, 2, 3]], True),
            ([[1]], [[1, 2, 3]], True),
            ([[1], [2]], [[1, 2, 3]], True),
            ([[1, 2, 3]], [[1, 2, 3]], True),

            ([[1, 2], [3]], [[1, 2], [3]], True),
            ([[1, 2], [3]], [[1, 2], [3, 4]], True),

            ([[4]], [[1, 2, 3]], False),
            ([[1, 4]], [[1, 2, 3]], False),

            ([[1, 2, 3]], [[1, 2], [3]], False),

        ]:
            one = RecursiveCollisionSet(frozenset(frozenset(i) for i in a))
            two = RecursiveCollisionSet(frozenset(frozenset(i) for i in b))

            self.assertEqual(one.subset(two), ans, f"{one.set} {two.set}")

    def test_merge(self):
        for a, b, ans in [
            ([], [[1, 2, 3]], [[1, 2, 3]]),
            ([[1]], [[1, 2, 3]], [[1, 2, 3]]),
            ([[1], [2]], [[1, 2, 3]], [[1, 2, 3]]),
            ([[1, 2, 3]], [[1, 2, 3]], [[1, 2, 3]]),

            ([[1, 2], [3]], [[1, 2], [3]], [[1, 2], [3]]),
            ([[1, 2], [3]], [[1, 2], [3, 4]], [[1, 2], [3, 4]]),
            ([[1, 2], [3]], [[1, 2], [3, 4]], [[1, 2], [3, 4]]),
            ([[1, 2], [3, 4]], [[1, 2], [3, 4]], [[1, 2], [3, 4]]),
            ([[1, 2], [3, 4, 5]], [[1, 2], [3, 4]], [[1, 2], [3, 4, 5]]),
            ([[1], [3, 4, 5]], [[1, 2], [3, 4]], [[1, 2], [3, 4, 5]]),

            ([[4]], [[1, 2, 3]], [[1, 2, 3], [4]]),
            ([[1, 4]], [[1, 2, 3]], [[1, 2, 3, 4]]),

            ([[1, 2, 3]], [[1, 2], [3]], [[1, 2, 3]]),

        ]:
            one = RecursiveCollisionSet(frozenset(frozenset(i) for i in a))
            two = RecursiveCollisionSet(frozenset(frozenset(i) for i in b))
            ans = RecursiveCollisionSet(frozenset(frozenset(i) for i in ans))

            self.assertEqual(ans, two.merge(one), f"{one.set} {two.set}")
            self.assertEqual(ans, one.merge(two), f"{one.set} {two.set}")


if __name__ == '__main__':
    unittest.main()
