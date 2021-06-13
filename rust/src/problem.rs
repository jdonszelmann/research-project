use crate::grid::Grid;
use crate::marked_coordinate::MarkedCoordinate;

pub struct Problem {
    pub(crate) grid: Grid,

    pub(crate) starts: Vec<MarkedCoordinate>,
    pub(crate) goals: Vec<MarkedCoordinate>,
}