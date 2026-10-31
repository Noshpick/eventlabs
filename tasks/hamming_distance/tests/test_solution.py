from solution import hamming_distance


def test_examples():
    assert hamming_distance(1, 4) == 2
    assert hamming_distance(3, 1) == 1


def test_zero_and_full():
    assert hamming_distance(0, 0) == 0
    assert hamming_distance(8, 7) == 4
