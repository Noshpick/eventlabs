# Dijkstra Shortest Path

Implement in `solution.py`:

```python
def dijkstra(n: int, edges: list[list[int]], src: int) -> list[float]:
    ...
```

`edges` holds directed weighted edges `[u, v, w]` (non-negative `w`). Return a
list of `n` shortest distances from `src`; use `float("inf")` for unreachable
nodes.

- `dijkstra(3, [[0, 1, 4], [0, 2, 1], [2, 1, 2]], 0)` -> `[0, 3, 1]`
