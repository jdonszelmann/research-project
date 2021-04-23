use crate::mapf::agent::Agent;
use crate::mapf::distance_heuristic::DistanceHeuristic;
use crate::mapf::graphlike::GraphLike;
use crate::mapf::mapf_problem::MAPFProblem;
use crate::mapf::{Location, MAPFAlgorithm, Path};
use std::collections::HashMap;
use std::rc::Rc;

pub struct AStarODID;

#[derive(Clone, Eq, PartialEq, Hash, Debug)]
struct State<AGENT> {
    agents: Vec<AGENT>,
}

#[derive(Clone, Eq, PartialEq, Hash, Debug)]
struct Node<AGENT> {
    parent: Option<Rc<Node<AGENT>>>,

    state: State<AGENT>,
}

// impl<AGENT> Node<AGENT> {
//     pub fn next() -> Vec<>
// }

impl<'a, ET, N, G, AGENT, DH> From<&'a MAPFProblem<ET, N, G, AGENT, DH>> for Node<AGENT> {
    fn from(p: &'a MAPFProblem<ET, N, G, AGENT, DH>) -> Self {
        Self {
            parent: None,
            state: todo!(),
        }
    }
}

/// At each time step an agent can either wait, or move to another location
#[derive(Copy, Clone, Debug)]
enum Action {
    Unset,
    Wait,
    MoveTo(Location),
}

impl Default for Action {
    fn default() -> Self {
        Self::Unset
    }
}

impl<ET, N, G: GraphLike<N, usize, ET>, AGENT: Agent, DH: DistanceHeuristic<N, usize, ET, G>>
    MAPFAlgorithm<ET, N, G, AGENT, DH> for AStarODID
{
    fn solve(problem: &MAPFProblem<ET, N, G, AGENT, DH>) -> HashMap<AGENT::Identifier, Path> {
        let initial_node = Rc::new(Node::from(problem));

        todo!()
    }
}
