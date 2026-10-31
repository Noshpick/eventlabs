# Coin Change

Implement in `solution.py`:

```python
def coin_change(coins: list[int], amount: int) -> int:
    ...
```

Return the fewest coins needed to make up `amount` (unlimited coins of each
denomination), or `-1` if it is impossible.

- `coin_change([1, 2, 5], 11)` -> `3` (5 + 5 + 1)
- `coin_change([2], 3)` -> `-1`
