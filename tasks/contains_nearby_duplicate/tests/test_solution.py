from solution import contains_nearby_duplicate as f


def test_true_cases():
    assert f([1, 2, 3, 1], 3) is True
    assert f([1, 0, 1, 1], 1) is True


def test_false_cases():
    assert f([1, 2, 3, 1, 2, 3], 2) is False
    assert f([1, 2, 3], 0) is False
