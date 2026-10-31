from solution import single_number


def test_examples():
    assert single_number([2, 2, 1]) == 1
    assert single_number([4, 1, 2, 1, 2]) == 4


def test_single_and_negative():
    assert single_number([1]) == 1
    assert single_number([-5, 3, 3]) == -5
