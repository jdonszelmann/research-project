use std::collections::HashMap;

use mapf_problem::MAPFProblem;

use crate::mapf::agent::Agent;
use petgraph::graph::NodeIndex;

pub mod grid;
pub mod agent;
pub mod astar_od_id;
pub mod mapf_problem;
pub mod distance_heuristic;
pub mod graphlike;

type Location = NodeIndex<u32>;


pub struct Path {
    path: Vec<Location>,
}

pub trait MAPFAlgorithm<ET, N, G, AGENT: Agent, DH> {
    fn solve(problem: &MAPFProblem<ET, N, G, AGENT, DH>) -> HashMap<AGENT::Identifier,  Path>;
}