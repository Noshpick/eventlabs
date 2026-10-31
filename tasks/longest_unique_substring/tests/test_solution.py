from solution import length_of_longest_substring as f


def test_examples():
    assert f("abcabcbb") == 3
    assert f("pwwkew") == 3


def test_uniform_and_empty():
    assert f("bbbbb") == 1
    assert f("") == 0


def test_full_range():
    assert f("abcdef") == 6
    assert f("dvdf") == 3
