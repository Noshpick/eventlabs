from solution import house_robber


def test_examples():
    assert house_robber([1, 2, 3, 1]) == 4
    assert house_robber([2, 7, 9, 3, 1]) == 12


def test_edge_cases():
    assert house_robber([]) == 0
    assert house_robber([5]) == 5
    assert house_robber([2, 1, 1, 2]) == 4
