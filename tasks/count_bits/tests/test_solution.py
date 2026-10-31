from solution import count_bits


def test_examples():
    assert count_bits(2) == [0, 1, 1]
    assert count_bits(5) == [0, 1, 1, 2, 1, 2]


def test_zero_and_power():
    assert count_bits(0) == [0]
    assert count_bits(8)[8] == 1
    assert count_bits(7) == [0, 1, 1, 2, 1, 2, 2, 3]
