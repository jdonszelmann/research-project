use crate::mapf::Location;
use std::hash::Hash;

pub trait Agent {
    type Identifier: Eq + PartialEq + Hash;

    fn location(&self) -> Location;
    fn set_location(&mut self, location: Location);

    fn goal(&self) -> Location;
    fn set_goal(&mut self, location: Location);

    fn identifier(&self) -> Self::Identifier;
}

pub struct SimpleAgent {
    location: Location,
    goal: Location,
    identifier: usize,
}

impl SimpleAgent {
    pub fn new(start_location: Location, goal: Location, identifier: usize) -> Self {
        Self {
            location: start_location,
            goal,
            identifier,
        }
    }
}

impl Agent for SimpleAgent {
    type Identifier = usize;

    fn location(&self) -> Location {
        self.location
    }

    fn set_location(&mut self, location: Location) {
        self.location = location;
    }

    fn goal(&self) -> Location {
        self.goal
    }

    fn set_goal(&mut self, location: Location) {
        self.goal = location;
    }

    fn identifier(&self) -> Self::Identifier {
        self.identifier
    }
}
