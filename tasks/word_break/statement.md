# Word Break

Implement in `solution.py`:

```python
def word_break(s: str, word_dict: list[str]) -> bool:
    ...
```

Return `True` if `s` can be segmented into a sequence of one or more words from
`word_dict`. Dictionary words may be reused.

- `word_break("leetcode", ["leet", "code"])` -> `True`
- `word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])` -> `False`
