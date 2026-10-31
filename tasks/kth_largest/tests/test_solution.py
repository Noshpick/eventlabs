from solution import kth_largest


def test_examples():
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4


def test_edges():
    assert kth_largest([1], 1) == 1
    assert kth_largest([7, 7, 7], 2) == 7
    assert kth_largest([-1, -5, 3], 3) == -5
