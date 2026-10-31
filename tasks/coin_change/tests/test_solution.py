from solution import coin_change


def test_examples():
    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change([2], 3) == -1


def test_zero_amount():
    assert coin_change([1], 0) == 0


def test_greedy_fails():
    assert coin_change([1, 5, 10, 25], 30) == 2
    assert coin_change([1, 3, 4], 6) == 2
