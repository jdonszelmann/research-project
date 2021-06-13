use crate::coordinate::Coordinate;
use std::ops::{Deref, DerefMut};

pub struct MarkedCoordinate {
    pub colour: i64,
    coordinate: Coordinate,
}

impl Deref for MarkedCoordinate {
    type Target = Coordinate;

    fn deref(&self) -> &Self::Target {
        &self.coordinate
    }
}

impl DerefMut for MarkedCoordinate {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.coordinate
    }
}
