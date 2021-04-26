# M*: A Complete Multirobot Path Planning Algorithm with PerformanceBounds

https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.221.1909&rep=rep1&type=pdf

## Subdimensional expansion

Collision free path of n robots in a common workspace W
Each robot has an obstacle free configuration space Q (so without walls)
which still contains collision states

* There is a collision function psi which is each pair of agents (i, j) which are in conflict 
with each other (on the same vertex or edge)
* This collision function extends to a joint configuration space of n agents, where it's
the union of individual collision functions
* The collision function also extends to paths, where it's the union of all collision functions
of states along the path.
  
idea: find a low(er) dimensional configuration space Q# embedded in Q which can be searched
by a planner (such as A star). As the planner searches Q# it will find information about 
collisions between robots, used to loaclly augment the dimensionality of Q#

Each agent finds an individually optimal path, being optimistic and assuming it is collision free.

## M*

Like A* but expansion does not consider every neighbor, only a limited set of neighbors





