from solution import binary_search


def test_found():
    assert binary_search([-1, 0, 3, 5, 9, 12], 9) == 4
    assert binary_search([-1, 0, 3, 5, 9, 12], -1) == 0


def test_not_found():
    assert binary_search([-1, 0, 3, 5, 9, 12], 2) == -1
    assert binary_search([], 1) == -1


def test_single():
    assert binary_search([5], 5) == 0
    assert binary_search([5], 3) == -1
