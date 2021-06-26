
# Matching in multi agent pathfinding 

Bachelor end project - Jonathan Donszelmann (Q4 academic year 2020/2021)

# Multi agent pathfinding

multi agent pathfinding (MAPF) is like pathfinding, but in a situation where the routes of 
multiple agents need to be planned simultaneously. During this planning, no collisions may
occur. To achieve this, a typical **A*** (a star) solver for MAPF will use a search space consisting
of the positions of all agents' positions at the same time. Each expansion will consider
every combination of new positions of all agents. The search space is many dimensional.
This leads to an exponential growth in compute time given a growing number of agents. MAPF is **pspace-hard**. 

## M* (m star)

M* is a more efficient algorithm than A* to solve MAPF. It uses subdimensional expansion (
refering to the many dimensional search space). M* assumes all agents are independent and tries
to plan a route for each agent independently according to an individually optimal policy (created
using A*). Only when it detects that agents *do* collide, will it combine planning for only these
colliding agents and in a sense locally increase the dimensionality of the search space.

# Paper

This repository is the source code used to gather results for a paper. This is my
bachelors project for the TU Delft. The paper can be found [here](tex/rendered/Research%20Project%20CSE3000%20final.pdf)
or in the TU Delft repositories [SOON]()

# Online benchmarks

Code in this repository is intended to integrate with the api provided by [mapf.nl](mapf.nl), 
also created by me (note: there used to be a token in the sourcecode of this repository. 
Please don't try to use this, it has been invalidated). This website also contains attempts
created by the algorithm in this repository

# Code

This repository contains the code for a simple A* implementation for MAPF, and multiple M* 
implementations. The original implementation of M* can be found in the [mstar folder](python/mstar)
but is pretty unreadable. It is important to note that this version is a heavily adapted version of
[James Ellis's repository](https://github.com/Jamesellis51015/Multi-Agent-Path-Finding-with-Reinforcement-Learning)

The version used for all benchmarks in the paper can be found in the [rewrite](python/mstar/rewrite)
folder and is a complete rewite of M* from the ground up. It supports recursive M* as well as operator
decomposition, and is highly configurable. It is also written *functionally*. A lot of the
confusing state which was previously held in a couple of god classes is now passed around in a much more
introspectable way.


# Benchmarks

As previously mentioned, all benchmarks are run with the version of M* which can be found [here](python/mstar/rewrite).
Benchmark code can be found in [the benchmarks folder](python/benchmarks). In this folder, python files
can be found which run entire benchmarks. Basically, there is one for each graph in the paper. Also all results
of these benchmarks can be found here (including raw data), and the exact maps on which benchmarks
were run. This was done in an effort to make results as reproducible as possible.

# License

Licensed under either of [Apache License, Version 2.0](LICENSE_APACHE) or [MIT license](LICENSE_MIT) at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this codebase, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions. 

