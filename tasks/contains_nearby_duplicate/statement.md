# Contains Nearby Duplicate

Implement in `solution.py`:

```python
def contains_nearby_duplicate(nums: list[int], k: int) -> bool:
    ...
```

Return `True` if there are two distinct indices `i` and `j` with
`nums[i] == nums[j]` and `abs(i - j) <= k`.

- `contains_nearby_duplicate([1, 2, 3, 1], 3)` -> `True`
- `contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)` -> `False`
