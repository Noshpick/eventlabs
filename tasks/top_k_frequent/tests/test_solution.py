from solution import top_k_frequent


def test_basic():
    assert set(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == {1, 2}


def test_single():
    assert set(top_k_frequent([1], 1)) == {1}


def test_three_counts():
    assert set(top_k_frequent([4, 4, 6, 6, 6, 5], 2)) == {6, 4}
