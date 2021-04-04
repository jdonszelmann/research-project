use std::marker::PhantomData;

use petgraph::EdgeType;

use crate::mapf::agent::Agent;
use crate::mapf::distance_heuristic::DistanceHeuristic;
use crate::mapf::graphlike::GraphLike;

pub struct MAPFProblem<G, ET, N, AGENT, DH> {
    pub graph: G,

    pub agents: Vec<AGENT>,

    pub distance_heuristic: DH,

    directed: PhantomData<ET>,
    node: PhantomData<N>,
}

impl<G, ET: EdgeType, N, AGENT: Agent, DH: DistanceHeuristic<N, usize, ET, G>> MAPFProblem<G, ET, N, AGENT, DH> where G: GraphLike<N, usize, ET> {
    pub fn new(graph: G, agents: Vec<AGENT>, distance_heuristic: DH) -> Self {
        Self {
            graph,
            agents,
            distance_heuristic,
            directed: Default::default(),
            node: Default::default(),
        }
    }
}

#[cfg(test)]
mod tests {
    use petgraph::Graph;

    use crate::mapf::mapf_problem::MAPFProblem;
    use crate::mapf::agent::SimpleAgent;
    use crate::mapf::grid::Grid;
    use crate::mapf::distance_heuristic::Trivial;

    #[test]
    fn test_with_graph() {
        let g = Graph::<(), usize>::new();

        // test if this compiles
        let _ = MAPFProblem::new(g, Vec::<SimpleAgent>::new(), Trivial);
    }

    #[test]
    fn test_with_grid() {
        let g = Grid::new(2, 2);

        // test if this compiles
        let _ = MAPFProblem::new(g, Vec::<SimpleAgent>::new(), Trivial);
    }
}