
# MMAPF

MMAPF is short for matching in multi-agent pathfinding.

## Multi agent pathfinding

[Stern, 2019](../tex/bibliography.bib) defines a multi agent pathfinding (or MAPF)
problem with `n` agents as the following tuple:

### Problem

`(G, s, t)` where: 
* `G` is a graph `(V, E)`
* `s` is numbered list of `k` vertices which are starting positions for each agent `a_i` 
* `g` is a numbered list of `k` vertices which are the terminal positions for each agent `a_i` 

When an agent reaches it's terminal position, it can either stay there (blocking
the way for other agents), or disappear, leaving a blank square through which
other agents can pass. Both approaches are used, but most MAPF definitions choose
for agents to choose at their target, including the papers written related to previous
research about MAPF with waypoints.

### Solution

Solving MAPF generates a set of `k` plans `{pi_1...pi_k}` which are routes for
each agent k to take through the graph `G`. All agents can move simultaneously.

## Conflicts

While agents `a_i` are traveling on their path `pi_i` there are certain conflicts
which may occur. The goal of MAPF is to avoid these conflicts:

* Edge conflict: two agents are on the same edge `E` at a timestep `t` (ie `pi_i[t] = pi_j[t]` and `pi_i[t+1] = pi_j[t+1]`)
* Vertex conflict: two agents are on the same vertex `V` at a timestep `t` (ie `pi_i[t] = pi_j[t]`) 
* Swapping: two agents swap vertices at a timestep `t` (ie `pi_i[t] = pi_j[t+1]` and `pi_i[t+1] = pi_j[t]`)
* Following conflict: an agent travels to a vertex from which another agent leaves in the same timestep (ie some `pi_i[t+1] = pi_j[t]` exists)
* Cycle conflict (implied by following conflict): a number of agents all swap vertices such that each of the agents lands on a vertex another agent in the set just left. 

NOTE 1: Not all these listed conflicts are always considered an actual conflict. Some
definitions of MAPF choose to omit for example the following conflict.  
NOTE 2: Some of these conflicts imply other conflicts. For example, forbidding vertex conflicts implies also 
forbidding edge conflicts.

### Goal

The goal of MAPF is to either
* Minimize the *sum of costs* of the paths `pi_i` for all agents `i`
* Minimize the cost of the longest path `pi_i` (or *makespan*)

## Cost funtion

The cost function for MAPF, we define like others do in for example [(Sharon, 2012)](../tex/bibliography.bib). 
Both waiting and moving one tile costs 1 unit, unless an agent is waiting on it's goal position and never leaving again.
This costs 0.

## Matching

For multi agent pathfinding with matching (MMAPF), the problem definition needs to be slightly altered. The new
definition is as follows:

`(G, s, g, sc, gc)` where:
* `G` is a graph `(V, E)`
* `s` is numbered list of `k` vertices which are starting positions for each agent `a_i`
* `sc` is a numbered list of `k` colors representing the color of each agent
* `g` is a numbered list of `l` vertices which are the terminal positions.
* `gc` is a numbered list of `l` colors representing the color of each terminal position

In this definition, terminal positions no longer belong to a single agent. Instead, any goal
position `g_i` which has the same color as an agent `a_i` is a terminal position for that agent.

The solution again consist of a set of `n` plans `{pi_1...pi_k}` for each agent `a_i`. And the goal
also is still to minimize either the *sum of costs* or the *makespan*.

## Choices

In the base problem, the size of s and the size of g (so k and l) need to be equal. 
Extension could choose not enforce this restriction. 

Both edge and vertex conflicts are forbidden. This automatically also rules out swapping conflicts. Following *is* allowed.

G is a unit grid



