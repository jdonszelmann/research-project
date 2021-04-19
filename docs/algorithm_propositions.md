# Propositions for algorithms to research

These are a set of base algorithms (without matching) which can be used to solve *MAPF*

## Conflict based search
[Sharon, G., Stern, R., Felner, A., & Sturtevant, N. R. (2015)](https://www.aaai.org/ocs/index.php/AAAI/AAAI12/paper/viewFile/5062/5239)

Computes a path for each agent independently. Detects conflicts
between pairs of agents by splitting the current solution into 
two related subproblems, each of which involves replanning a single agent. 
Recursively resolving conflicts by splitting a subproblem into two children implicitly
defines a search tree. The high-level search explores this
tree using best-first search and terminates when it expands
a collision-free leaf.

## Branch and cut and price
[Lam, E., Le Bodic, P., Harabor, D. D., & Stuckey, P. J. (2019)](https://harabor.net/data/papers/llhs-bcpfmapf-ijcai19.pdf)

## A* + Independence detection + Operator decomposition

[Standley, T. (2010)](https://www.cs.huji.ac.il/~jeff/aaai10/02/AAAI10-039.pdf)

properties: optimal

Use A* for each agent to find a path from their
start to finish. Operator decomposition adds to 
this by searching through the possible moves of 
other agents too every time step. A* searches 
operators (legal moves for agents like wait, N, S, E, W)
and each time step advances one agent.

An admissible heuristic for this A*+OD can be the sum
of all optimal paths for each agent individually.

This algorithm (A*+OD) is still exponential on the 
number of agents. With independence detection, an
attempt is made to detect if two agents (or groups 
of agents) are independent in their path. If this
is a case, their A* (+OD) can be solved independently
from the other agents as they have been proven to never
interfere.

## M*

[Wagner, G., & Choset, H. (2011, September)](https://ieeexplore-ieee-org.tudelft.idm.oclc.org/document/6095022)

properties: complete, optimal

Similar to A*, but instead of considering all neighbours 
in the expansion step, M* only considers the *limited neighbors*
which can be reached while moving each robot according to its individually optimal policy.

Backpropagation is used to keep the collion sets updated.

## Increasing Cost Tree Search (ICTS)
[Sharon, G., Stern, R., Goldenberg, M., & Felner, A. (2013)](https://people.engr.tamu.edu/guni/Papers/ICTS-IJCAI11.pdf)

Built upon the understanding that a *complete* solution for the 
entire problem is built from individual paths for each agent.
We build a tree in which each node is composed of the optimal path costs of all agents
assuming no other agents exist. There is a goal node if there is a non-conflicting
solution for each agent.
