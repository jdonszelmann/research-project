use crate::mapf::agent::Agent;
use crate::mapf::distance_heuristic::DistanceHeuristic;
use crate::mapf::graphlike::GraphLike;
use crate::mapf::mapf_problem::MAPFProblem;
use crate::mapf::{Location, MAPFAlgorithm, Path};
use std::collections::{HashMap, HashSet};
use std::rc::Rc;
use petgraph::csr::NodeIndex;

pub struct MStar;


impl<ET, N, G: GraphLike<N, usize, ET>, AGENT: Agent, DH: DistanceHeuristic<N, usize, ET, G>>
MAPFAlgorithm<ET, N, G, AGENT, DH> for MStar
{
    fn solve(problem: &MAPFProblem<ET, N, G, AGENT, DH>) -> HashMap<AGENT::Identifier, Path> {
        let max_node_index = problem.graph.graph().node_indices().map(|i| i.index()).max().unwrap_or(0);

        let mut collision_sets = vec![HashSet::new(), max_node_index];
        let mut costs = vec![u64::MAX, max_node_index];
        let mut back_ptrs = vec![todo!(), max_node_index];

        // let initial =

        todo!()
    }
}
