from solution import missing_number


def test_examples():
    assert missing_number([3, 0, 1]) == 2
    assert missing_number([0, 1]) == 2


def test_longer():
    assert missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8


def test_missing_zero():
    assert missing_number([1]) == 0
    assert missing_number([0]) == 1
