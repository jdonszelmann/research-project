# Project summary


## *Tuss*

* NS Trains are parked on a *shunting yard* at night
* Routing of trains to this *shunting yard* is an NP-Hard planning 
problem called the Train Unit Shunting and Servicing (*TUSS*) problem.
* Question: What's the capacity of such a shunting yard?
    * lower bounds can be created by using local search heuristics. 
    This heuristic can fail.
    * loose upper bounds exist by for example measuring the total amount
    of tracks in the shunting yard. 
    (is this true? *we suspect* in original project definition)

* Because routing is also a part of *TUSS*, it is suspected that 
considering this will result in (much) better upper bounds.
* Consider relaxed version of *TUSS*. If no exact solution can be found to this
then this must be an upper bound. (Think about it like this. If no solution can 
be found for a version of the problem which allows a certain number of trains in 
the yard, then the actual number of trains which can fit in the yard must be less)

## *MAPF*

* Multi agent pathfinding is an algorithm which tries to find paths on a graph
for a number of agents. Agents are scheduled in such a way that they do not collide.
    * *SIC* (sum of individual costs) is the sum of the costs of the path of each agent
    * *makespan* is the largest cost of the path, out of all agents
    * Usually one of these is minimized (obviously)
* [(Stern et al, 2019)](../tex/bibliography.bib)
* Basis for routing in the *TUSS* problem
* Caveat: cannot be used standalone. *Matching* needs to be used.
    * Departures (and I imagine arrivals) do not specify a single train (or agent in *MAPF*)
    * Instead a *train type* is specified.
    * This is a matching problem, linking departure (and arrival?) slots to train types.
    
