
#[macro_use] extern crate impl_ops;

mod coordinate;
mod grid;
mod marked_coordinate;
mod problem;
mod api;
mod algorithm;
mod solution;

pub fn main() {
    let res = api::run();
}
