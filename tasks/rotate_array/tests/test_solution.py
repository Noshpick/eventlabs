from solution import rotate_array


def test_basic():
    assert rotate_array([1, 2, 3, 4, 5, 6, 7], 3) == [5, 6, 7, 1, 2, 3, 4]
    assert rotate_array([-1, -100, 3, 99], 2) == [3, 99, -1, -100]


def test_k_larger_than_len():
    assert rotate_array([1, 2], 3) == [2, 1]


def test_no_mutation_and_zero():
    data = [1, 2, 3]
    assert rotate_array(data, 0) == [1, 2, 3]
    assert data == [1, 2, 3]
    assert rotate_array([], 5) == []
