from solution import first_unique_char


def test_examples():
    assert first_unique_char("leetcode") == 0
    assert first_unique_char("loveleetcode") == 2


def test_none_and_empty():
    assert first_unique_char("aabb") == -1
    assert first_unique_char("") == -1


def test_late_unique():
    assert first_unique_char("aabbcdd") == 4
