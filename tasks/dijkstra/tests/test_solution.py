from solution import dijkstra


def test_example():
    assert dijkstra(3, [[0, 1, 4], [0, 2, 1], [2, 1, 2]], 0) == [0, 3, 1]


def test_unreachable():
    dist = dijkstra(2, [], 0)
    assert dist[0] == 0
    assert dist[1] == float("inf")


def test_longer():
    assert dijkstra(4, [[0, 1, 1], [1, 2, 2], [0, 2, 5], [2, 3, 1]], 0) == [0, 1, 3, 4]
