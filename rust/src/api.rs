use num_traits::{Unsigned, PrimInt};
use crate::problem::Problem;
use thiserror::Error;
use reqwest::blocking::Client;
use reqwest::{Method, Url};
use serde::{Serialize, Deserialize};
use crate::grid::Grid;
use crate::algorithm::MapfmAlgorithm;
use crate::solution::Solution;


pub struct ProblemIdentifier {
    id: usize,
    debug: bool,
    url: String,
    token: String,
}

#[derive(Debug, Error)]
pub enum RunError<A: MapfmAlgorithm> {
    Reqwest(#[from] reqwest::Error),
    Algorithm(#[from] <A as MapfmAlgorithm>::Error),
}


fn get_problem(algorithm_name: &str, algorithm_version: &str, problem_identifier: &ProblemIdentifier) -> Result<(Problem, usize), RunError> {
    let url = Url::parse(&problem_identifier.url)?
        .join(&format!("/api/benchmark/attempt/{}", problem_identifier.id))?;

    let client = Client::new();

    #[derive(Serialize, Deserialize)]
    struct RequestData<'a, 'b> {
        algorithm: &'a str,
        version: &'b str,
        debug: bool,
    }

    #[derive(Serialize, Deserialize)]
    struct ResponseMarkedCoordinate {
        x: i64,
        y: i64,
        color: i64,
    }

    #[derive(Serialize, Deserialize)]
    struct ResponseData {
        grid: Vec<Vec<i64>>,
        width: usize,
        height: usize,

        starts: Vec<ResponseMarkedCoordinate>,
        goals: Vec<ResponseMarkedCoordinate>,

        attempt_id: usize,
    }

    let data = RequestData {
        algorithm: algorithm_name,
        version: algorithm_version,
        debug: problem_identifier.debug,
    };

    let req = client.post(url)
        .json(&data)
        .header("X-API-Token", &problem_identifier.token)
        .build()?;

    let res = client.execute(req)?;

    let data: ResponseData = res.json()?;

    Ok((Problem {
        grid: Grid::from_int_vecs(data.width, data.height, data.grid),
        starts: vec![],
        goals: vec![]
    }, data.attempt_id))
}

pub fn run(algorithm: &impl MapfmAlgorithm, problem_identifier: &ProblemIdentifier) -> Result<RunError, Solution> {
    let (problem, attempt_id) = get_problem(
        algorithm.name(),
        algorithm.version(),
        problem_identifier,
    )?;

    let solution = algorithm.solve(problem)?;
}