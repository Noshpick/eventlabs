# Climbing Stairs

Implement in `solution.py`:

```python
def climb_stairs(n: int) -> int:
    ...
```

You climb a staircase of `n` steps, taking either 1 or 2 steps at a time. Return
the number of distinct ways to reach the top.

- `climb_stairs(2)` -> `2`, `climb_stairs(3)` -> `3`
- `1 <= n <= 45` — recursion without memoization will be too slow.
