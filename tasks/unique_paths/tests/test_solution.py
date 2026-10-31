from solution import unique_paths


def test_examples():
    assert unique_paths(3, 7) == 28
    assert unique_paths(3, 2) == 3


def test_symmetry_and_degenerate():
    assert unique_paths(7, 3) == 28
    assert unique_paths(1, 1) == 1
    assert unique_paths(1, 10) == 1
