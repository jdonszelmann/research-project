use crate::mapf::{MAPFAlgorithm, Path, Location};
use crate::mapf::agent::Agent;
use std::collections::HashMap;
use crate::mapf::mapf_problem::MAPFProblem;
use crate::mapf::distance_heuristic::DistanceHeuristic;
use crate::mapf::graphlike::GraphLike;

pub struct AStarODID;

enum StateType {
    Standard,
    Intermediate
}

struct State<AGENT> {
    agents: Vec<AGENT>,

    state_type: StateType,
}

/// At each time step an agent can either wait, or move to another location
enum Actions {
    Wait,
    MoveTo(Location)
}

impl<ET, N, G: GraphLike<N, usize, ET>, AGENT: Agent, DH: DistanceHeuristic<N, usize, ET, G>> MAPFAlgorithm<ET, N, G, AGENT, DH> for AStarODID {
    fn solve(problem: &MAPFProblem<ET, N, G, AGENT, DH>) -> HashMap<AGENT::Identifier, Path> {

        todo!()
    }
}

