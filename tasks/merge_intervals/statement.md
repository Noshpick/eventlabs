# Merge Intervals

Implement in `solution.py`:

```python
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    ...
```

Merge all overlapping intervals and return the result sorted by start.

- `merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])` -> `[[1, 6], [8, 10], [15, 18]]`
- Touching intervals count as overlapping: `[1, 4]` and `[4, 5]` merge into `[1, 5]`.
