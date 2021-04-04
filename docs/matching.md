
# Matching (graph theory)

This section is inspired by the [wikipedia article](https://en.wikipedia.org/wiki/Matching_(graph_theory)) 
about matching.

A matching is a set of edges. In a matching no two edges share a common vertex
None of the edges may be loops.

If a vertex is an endpoint of any of the vertices in the matching,
this vertex is *matched* (sometimes called saturated).

A *maximal* (not maximum!) matching is a matching
which is not a subset of another matching. ie. there is 
no other set of edges which still has all the properties of a 
matching, but is a strict superset of this matching.

A *maximum* (not maximal!) matching is a matching
containing the largest number of edges. Multiple such
matchings may exist. Every *maximum* matching is also *maximal*.

The size of a matching is the number of edges in the matching. 
The *matching number* of a graph is the size of a *maximum matching* of that graph.

A *perfect* (or *complete*) matching is a matching containing every vertex of a 
graph. A perfect matching is *maximum* and *maximal*. A perfect matching 
can only exist on graphs with an even number of vertices. 

The *matching number* of graphs with a *perfect* matching is `|V| / 2` 
(half the number of vertices in the graph.)

# Matching on bipartite graphs

This section is my own addition and not based on the before mentioned
Wikipedia article.

On bipartite graphs, matching is interesting. This is because a matching
on such graph represents a set of connections between the two parts of the
bipartite graph such that no edge is used twice. This is important for *TUSS*

# Types of matchings on bipartite graphs

This section is again inspired by the [wikipedia article](https://en.wikipedia.org/wiki/Matching_(graph_theory)) 
about matching.

| Type | description | Algorithm |
| --- | --- | --- | 
| Maximum-cardinality matching | Find a matching with as many edges as possible (*maximum* matching) | `O(sqrt(V) * E)` ([Hopcroft-Karp algorithm](https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm)) |
| Maximum-weight matching (assignment problem) | Find a matching on a weighted graph with the largest weight | `O(V^2 * E)` or `O(V^2 * log V + V*E)` ([Hungarian algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm)) | 
| Maximal matching | Find a maximal matching for a graph. | Trivial but no polynomial algorithm to find a minimum maxial matching |

Online matching is possible (Karp et al, 1990).