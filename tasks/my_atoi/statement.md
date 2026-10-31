# String to Integer (atoi)

Implement in `solution.py`:

```python
def my_atoi(s: str) -> int:
    ...
```

Parse leading whitespace, an optional sign, then digits. Stop at the first
non-digit. Return 0 if no digits were read. Clamp the result to the signed
32-bit range `[-2**31, 2**31 - 1]`.

- `my_atoi("   -42")` -> `-42`
- `my_atoi("4193 with words")` -> `4193`
