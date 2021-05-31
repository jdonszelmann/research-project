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



if __name__ == '__main__':
    unittest.main()
