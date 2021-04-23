
# Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks

https://arxiv.org/pdf/1906.08291.pdf

[Our own definition derived from this](../mapfm_definition.md)

Establishes a definition for MAPF which we used for our own definition
Establishes a set of benchmarks

Establishes a list of variations on MAPF:

* Large agents: geometric shape of agents matters
* Kinematic constraints: things like velocity and acceleration of agents matter
* Tasks and agents (I think this is close to what we are researching with MAPFM)
    * Anonymous MAPF: Any agent can go to any target (MAPFM with one color, solvable in polynomial time)
    * Colored MAPF: ([Ma  and  Koenig 2016](delay_probabilities.md);  Solovey  and  Halperin  2014) MAPFM exactly!
    * online MAPF: agents can get new targets after reaching old targets. Continuous
* MAPF on weighted graphs
