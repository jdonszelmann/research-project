use petgraph::{Graph, Undirected};
use std::collections::HashMap;
use crate::mapf::Location;
use crate::mapf::graphlike::GraphLike;

pub struct Grid {
    pub graph: Graph<(usize, usize), usize, Undirected>,
    n: usize,
    m: usize,

    map: HashMap<(usize, usize), Location>,
}

impl Grid {
    pub fn new<>(n: usize, m: usize) -> Self {
        let mut graph = Graph::new_undirected();
        let mut map = HashMap::new();

        for i in 0..n {
            for j in 0..m {
                let location = graph.add_node((i, j));

                if i > 0 {
                    // Safety: This node was inserted earlier so is always in the map
                    graph.add_edge(*map.get(&(i-1, j)).unwrap(), location, 1);
                }

                if j > 0 {
                    // Safety: This node was inserted earlier so is always in the map
                    graph.add_edge(*map.get(&(i, j-1)).unwrap(), location, 1);
                }

                map.insert((i, j), location);
            }
        }

        Self {
            n,
            m,
            graph,
            map,
        }
    }

    pub fn node_at(&self, i: usize, j: usize) -> Option<Location> {
        self.map.get(&(i, j)).map(|i| *i)
    }
}


impl GraphLike<(usize, usize), usize, Undirected> for Grid {
    fn graph(&self) -> &Graph<(usize, usize), usize, Undirected, u32> {
        &self.graph
    }

    fn graph_mut(&mut self) -> &mut Graph<(usize, usize), usize, Undirected, u32> {
        &mut self.graph
    }
}


#[cfg(test)]
mod tests {
    use crate::mapf::grid::Grid;
    use crate::mapf::graphlike::GraphLike;

    #[test]
    pub fn heuristic () {
        for i in 1..10 {
            for j in 1..10 {
                let g = Grid::new(i, j);
                assert_eq!(g.graph().edge_count(), (i - 1) * j + (j-1) * i);
                assert_eq!(g.graph().node_count(), i * j);
            }
        }
    }

    #[test]
    pub fn test_grid_edge_count () {
        for i in 1..10 {
            for j in 1..10 {
                let g = Grid::new(i, j);
                assert_eq!(g.graph().edge_count(), (i - 1) * j + (j-1) * i);
                assert_eq!(g.graph().node_count(), i * j);
            }
        }
    }

    #[test]
    pub fn test_grid_neighbors () {
        for i in 1..10 {
            for j in 1..10 {
                let g = Grid::new(i, j);

                for x in 0..i {
                    for y in 0..j {
                        let idx = g.node_at(x, y).unwrap();
                        let neighbors = g.graph().neighbors(idx);

                        let mut sides = [false; 4];

                        if x == 0 {
                            sides[0] = true;
                        }

                        if x == i - 1 {
                            sides[1] = true;
                        }

                        if y == 0 {
                            sides[2] = true;
                        }

                        if y == j - 1 {
                            sides[3] = true;
                        }

                        for n in neighbors {
                            let (a, b) = g.graph().node_weight(n).unwrap();

                            if x > 0 && (*a, *b) == (x-1, y) {
                                sides[0] = true;
                            }
                            if x < i - 1 && (*a, *b) == (x+1, y) {
                                sides[1] = true;
                            }
                            if y > 0 && (*a, *b) == (x, y-1) {
                                sides[2] = true;
                            }
                            if y < j - 1 && (*a, *b) == (x, y+1) {
                                sides[3] = true;
                            }
                        }

                        assert_eq!(sides.iter().filter(|&&i| i).count(), 4);
                    }
                }
            }
        }
    }
}
