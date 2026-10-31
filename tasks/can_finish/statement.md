# Course Schedule

Implement in `solution.py`:

```python
def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:
    ...
```

Each pair `[a, b]` means course `a` requires course `b` first. Return `True` if
all courses can be finished, i.e. the dependency graph has no cycle.

- `can_finish(2, [[1, 0]])` -> `True`
- `can_finish(2, [[1, 0], [0, 1]])` -> `False`
