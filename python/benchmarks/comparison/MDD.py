from collections import defaultdict
from collections import deque


class MDD:
    def __init__(self, my_map, agent, start, goal, depth, generate=True, last_mdd=None):
        """ Note that in order to save memory, we do not store the map on each
        MDD, but instead pass the map as an argument to the generation function"""
        self.agent = agent
        self.start = start
        self.goal = goal
        self.depth = depth
        self.mdd = None
        self.level = defaultdict(set)
        self.bfs_tree = {}
        if generate:
            if last_mdd and last_mdd.depth < depth and last_mdd.agent == agent:
                self.generate_mdd(my_map, last_mdd)
            else:
                self.generate_mdd(my_map)

    def generate_mdd(self, my_map, last_mdd=None):
        if last_mdd:
            bfs_tree = self.bootstrap_depth_d_bfs_tree(my_map, self.start, self.depth, last_mdd.bfs_tree)
        else:
            bfs_tree = self.get_depth_d_bfs_tree(my_map, self.start, self.depth)
        self.bfs_tree = bfs_tree
        mdd = self.bfs_to_mdd(bfs_tree['tree'], self.start, self.goal, self.depth)
        self.mdd = mdd
        if mdd:
            self.populate_levels(self.mdd)

    def populate_levels(self, mdd):
        self.level[0] = {self.start}
        for adjacent in mdd.values():
            for node in adjacent:
                self.level[node[1]].add(node[0])

    def get_depth_d_bfs_tree(self, my_map, start, depth):
        # Run BFS to depth 'depth' to find the solutions for this agent
        fringe = deque()
        fringe.append((start, 0))
        prev_dict = defaultdict(set)
        visited = set()
        bfs_tree = self.main_bfs_loop(my_map, start, depth, fringe, prev_dict, visited)
        return bfs_tree

    def bootstrap_depth_d_bfs_tree(self, my_map, start, depth, old_tree):
        fringe = deque()
        old_fringe = list(old_tree['fringe'])
        old_fringe.sort(key=lambda x: x[0][0] + x[0][1])
        fringe.extend(old_fringe)
        prev_dict = old_tree['tree']
        for node in old_fringe:
            node_prevs = old_tree['fringe_prevs'][node]
            prev_dict[node].update(node_prevs)
        visited = old_tree['visited']
        new_bfs_tree = self.main_bfs_loop(my_map, start, depth, fringe, prev_dict, visited)
        return new_bfs_tree

    def main_bfs_loop(self, my_map, start, depth, fringe, prev_dict, visited):
        depth_d_plus_one_fringe = set()
        fringe_prevs = defaultdict(set)
        while fringe:
            curr = fringe.popleft()
            loc, d = curr
            children = self.get_valid_children(my_map, loc, d)
            for c in children:
                if c[1] <= depth:
                    prev_dict[c].add(curr)
                    if c not in visited:
                        fringe.append(c)
                        visited.add(c)
                if c[1] == depth + 1:
                    depth_d_plus_one_fringe.add(c)
                    fringe_prevs[c].add(curr)
        return {'tree': prev_dict, 'visited': visited, 'depth': depth, 'fringe': depth_d_plus_one_fringe,
                'fringe_prevs': fringe_prevs}

    def bfs_to_mdd(self, bfs_tree, start, goals, depth):
        # Convert a complete bfs tree to an mdd
        # Quality code xD
        if isinstance(goals, int):
            goals = [goals]
        goal_times = [(goal, depth) for goal in goals]
        visited = set()
        mdd = defaultdict(set)
        trace_list = deque()
        for goal_time in goal_times:
            for parent in bfs_tree[goal_time]:
                trace_list.append((parent, goal_time))
                visited.add((parent, goal_time))
            while trace_list:
                curr, child = trace_list.popleft()
                mdd[curr].add(child)
                for p in bfs_tree[curr]:
                    if (p, curr) not in visited:
                        visited.add((p, curr))
                        trace_list.append((p, curr))
        return mdd

    def get_valid_children(self, my_map, loc, d):
        # Get all children that are on the map
        good_children = [(loc, d + 1)]
        for c in my_map[loc]:
            good_children.append((c, d + 1))
        return good_children
