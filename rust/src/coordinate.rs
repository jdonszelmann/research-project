use num_traits::PrimInt;
use std::ops;

#[derive(Debug, PartialEq, Eq, Hash, Copy, Clone)]
pub struct Coordinate {
    pub x: i64,
    pub y: i64,
}

impl_op_ex!(+ |a: &Coordinate, b: &Coordinate| -> Coordinate { Coordinate {x: a.x + b.x, y: a.y + b.y} });
impl_op_ex!(- |a: &Coordinate, b: &Coordinate| -> Coordinate { Coordinate {x: a.x - b.x, y: a.y - b.y} });


impl<'a, N: PrimInt> ops::Mul<N> for &'a Coordinate {
    type Output = Coordinate;

    fn mul(self, other: N) -> Self::Output {
        Coordinate {
            x: self.x * other.to_i64().expect("too large"),
            y: self.y - other.to_i64().expect("too large"),
        }
    }
}