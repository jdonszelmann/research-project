use crate::problem::Problem;
use std::error::Error;
use std::fmt::Debug;
use crate::solution::Solution;


pub trait MapfmAlgorithm {
    type Error: Error + Debug;

    fn name() -> &'static str;
    fn version() -> &'static str {
        "0.0.1"
    }

    fn solve(problem: Problem) -> Result<Solution, Self::Error>;
}