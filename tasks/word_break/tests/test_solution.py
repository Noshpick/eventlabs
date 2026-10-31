from solution import word_break


def test_true_cases():
    assert word_break("leetcode", ["leet", "code"]) is True
    assert word_break("applepenapple", ["apple", "pen"]) is True


def test_false_cases():
    assert word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False


def test_empty_string():
    assert word_break("", ["a"]) is True
