
# Meta-Agent Conflict-Based Search For Optimal Multi-Agent Path Finding

https://people.engr.tamu.edu/guni/Papers/SOCS12-MACBS.pdf

Defines a cost function similar to [ours](../mapfm_definition.md) (where waiting also costs 1 unit)

Solving mapf:
coupled approach : each agent's path is planned seperately - faster but not always optimal
decoupled approach : all agent's paths are planned together - usually optimal but slower

Meta agents: when the number of conflicts of agents are higher than some bound, their planning is merged into one meta
agent and planned together. This solves some issues with CBS where it can be exponentially slower than A* in some cases.

They call it the best of both worlds between A* with independence detection, and CBS.


