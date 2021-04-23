use crate::traintype::TrainType;

#[derive(Debug, Eq, PartialEq, Hash)]
pub struct Train {
    train_type: TrainType,
}

impl Train {
    pub fn new(train_type: TrainType) -> Self {
        Train { train_type }
    }
}
