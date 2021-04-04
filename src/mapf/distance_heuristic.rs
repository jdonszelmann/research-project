use crate::mapf::Location;
use petgraph::EdgeType;
use crate::mapf::graphlike::GraphLike;

/// A heuristic for the distance between two nodes in the graph.
pub trait DistanceHeuristic<N, E, ET, G: GraphLike<N, E, ET>> {
    /// Return an estimate for the distance between from and to.
    /// This distance needs to be an optimistic estimate (ie less than or equal
    /// to the true distance) for users of the heuristic to guarantee optimality.
    fn heuristic(graph: G, from: Location, to: Location) -> f64;
}


pub struct Trivial;
impl<N, E, ET, G: GraphLike<N, E, ET>> DistanceHeuristic<N, E, ET, G> for Trivial {
    fn heuristic(_graph: G, _from: Location, _to: Location) -> f64 {
        0.0
    }
}


pub struct Manhattan;
impl<A, E, ET: EdgeType, G: GraphLike<(A, A), E, ET>> DistanceHeuristic<(A, A), E, ET, G> for Manhattan
    where A: Copy + Clone + num::Num + Ord + num::ToPrimitive {
    fn heuristic(graph: G, from: Location, to: Location) -> f64 {
        let (x1, y1) = *graph.graph().node_weight(from).expect("Location not in graph");
        let (x2, y2) = *graph.graph().node_weight(to).expect("Location not in graph");

        let dx = x1.max(x2) - x1.min(x2);
        let dy = y1.max(y2) - y1.min(x2);

        (dx + dy).to_f64().expect("couldn't convert to float")
    }
}

pub struct Euclidean;
impl<A, E, ET: EdgeType, G: GraphLike<(A, A), E, ET>> DistanceHeuristic<(A, A), E, ET, G> for Euclidean
    where A: Copy + Clone + num::Num + Ord + num::ToPrimitive {
    fn heuristic(graph: G, from: Location, to: Location) -> f64 {
        let (x1, y1) = *graph.graph().node_weight(from).expect("Location not in graph");
        let (x2, y2) = *graph.graph().node_weight(to).expect("Location not in graph");

        let dx = x1.max(x2) - x1.min(x2);
        let dy = y1.max(y2) - y1.min(x2);

        let dxf: f64 = dx.to_f64().expect("couldn't convert to float");
        let dyf: f64 = dy.to_f64().expect("couldn't convert to float");

        (dxf * dxf + dyf * dyf).sqrt()
    }
}

#[cfg(test)]
mod tests {
    use crate::mapf::grid::Grid;
    use crate::mapf::distance_heuristic::{Manhattan, DistanceHeuristic, Euclidean};

    #[test]
    fn test_manhattan() {
        let g = Grid::new(5, 5);
        let n1 = g.node_at(0, 0).unwrap();
        let n2 = g.node_at(1, 1).unwrap();

        assert_eq!(Manhattan::heuristic(g, n1, n2), 2.0);
    }

    #[test]
    fn test_euclidean() {
        let g = Grid::new(5, 5);
        let n1 = g.node_at(0, 0).unwrap();
        let n2 = g.node_at(1, 1).unwrap();

        assert_eq!(Euclidean::heuristic(g, n1, n2), 2.0f64.sqrt());
    }
}