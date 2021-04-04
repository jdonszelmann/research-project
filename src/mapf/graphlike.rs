use petgraph::Graph;

pub trait GraphLike<N, E, ET> {
    fn graph(&self) -> &Graph<N, E, ET>;
    fn graph_mut(&mut self) -> &mut Graph<N, E, ET>;
}

impl<N, E, ET> GraphLike<N, E, ET> for Graph<N, E, ET> {
    fn graph(&self) -> &Graph<N, E, ET> {
        self
    }

    fn graph_mut(&mut self) -> &mut Graph<N, E, ET>  {
        self
    }
}