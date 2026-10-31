from solution import can_finish


def test_examples():
    assert can_finish(2, [[1, 0]]) is True
    assert can_finish(2, [[1, 0], [0, 1]]) is False


def test_chain_and_empty():
    assert can_finish(4, [[1, 0], [2, 1], [3, 2]]) is True
    assert can_finish(3, []) is True


def test_long_cycle():
    assert can_finish(4, [[0, 1], [1, 2], [2, 3], [3, 0]]) is False
