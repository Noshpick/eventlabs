# FizzBuzz Sum

Implement in `solution.py`:

```python
def fizzbuzz_sum(n: int) -> int:
    ...
```

Return the sum of all integers in `[1, n]` that are divisible by 3 or 5,
but **count numbers divisible by both only once**.

- `fizzbuzz_sum(10)` → 3 + 5 + 6 + 9 + 10 = `33`
- `1 <= n <= 10**9` — a loop is too slow for the largest test; use a formula.
