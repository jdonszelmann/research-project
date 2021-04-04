# Propositions for algorithms to research

These are a set of base algorithms (without 
matching) which can be used to solve *MAPF*

## Conflict based search

## Branch and cut and price

## A* + Independence detection + Operator decomposition

[(Standley, 2010)](../tex/bibliography.bib)

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

[(Wagner et al, 2011)](../tex/bibliography.bib)

properties: complete, optimal

