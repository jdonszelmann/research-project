
# MMAPF

MMAPF is short for matching in multi-agent pathfinding.

## Multi agent pathfinding

[Stern, 2019](../tex/bibliography.bib) defines a multi agent pathfinding (or MAPF)
problem with `n` agents as the following tuple:

### Problem

`(G, s, t)` where: 
* `G` is a graph `(V, E)`
* `s` is numbered list of `n` vertices which are starting positions for each agent `a_i` 
* `t` is a numbered list of `n` vertices which are the terminal positions for each agent `a_i` 

When an agent reaches it's terminal position, it can either stay there (blocking
the way for other agents), or disappear, leaving a blank square through which
other agents can pass. Both approaches are used, but most MAPF definitions choose
for agents to choose at their target, including the papers written related to previous
research about MAPF with waypoints.

### Solution

Solving MAPF generates a set of `n` plans `{pi_1...pi_k}` which are routes for
each agent k to take through the graph `G`. All agents can move simultaneously.

## Conflicts

While agents `a_i` are traveling on their path `pi_i` there are certain conflicts
which may occur. The goal of MAPF is to avoid these conflicts:

* Edge conflict: two agents are on the same edge `E` at a timestep `x` (ie `pi_i[x] = pi_j[x]` and `pi_i[x+1] = pi_j[x+1]`)
* Vertex conflict: two agents are on the same vertex `V` at a timestep `x` (ie `pi_i[x] = pi_j[x]`) 
* Swapping: two agents swap vertices at a timestep `x` (ie `pi_i[x] = pi_j[x+1]` and `pi_i[x+1] = pi_j[x]`)
* Following conflict: an agent travels to a vertex from which another agent leaves in the same timestep (ie some `pi_i[x+1] = pi_j[x]` exists)
* Cycle conflict (implied by following conflict): a number of agents all swap vertices such that each of the agents lands on a vertex another agent in the set just left. 

NOTE 1: Not all these listed conflicts are always considered an actual conflict. Some
definitions of MAPF choose to omit for example the following conflict.  
NOTE 2: Some of these conflicts imply other conflicts. For example, forbidding vertex conflicts implies also 
forbidding edge conflicts.

### Goal

The goal of MAPF is to either
* Minimize the *sum of costs* of the paths `pi_i` for all agents `i`
* Minimize the cost of the longest path `pi_i` (or *makespan*)

## Matching

For multi agent pathfinding with matching (MMAPF), the problem definition needs to be slightly altered. The new
definition is as follows:

`(G, s, t, sc, tc)` where:
* `G` is a graph `(V, E)`
* `s` is numbered list of `n` vertices which are starting positions for each agent `a_i`
* `sc` is a numbered list of `n` colors representing the color of each agent
* `t` is a numbered list of `m` vertices which are the terminal positions.
* `tc` is a numbered list of `m` colors representing the color of each terminal position

In this definition, terminal positions no longer belong to a single agent. Instead, any terminal
position `t_i` which has the same color as an agent `a_i` is a terminal position for that agent.

The solution again consist of a set of `n` plans `{pi_1...pi_k}` for each agent `a_i`. And the goal
also is still to minimize either the *sum of costs* or the *makespan*.

### Open questions

* Is a problem with `n < m` allowed?
* Is a problem with `n > m` allowed?



