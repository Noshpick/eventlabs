# LRU Cache

Implement in `solution.py` a class:

```python
class LRUCache:
    def __init__(self, capacity: int): ...
    def get(self, key: int) -> int: ...
    def put(self, key: int, value: int) -> None: ...
```

A least-recently-used cache: `get` returns the value or `-1` and marks the key
as recently used; `put` inserts or updates and evicts the least recently used
key when over capacity. Both operations in O(1).
