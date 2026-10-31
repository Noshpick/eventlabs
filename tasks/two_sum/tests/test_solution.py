from solution import two_sum


def test_basic():
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)


def test_negative_numbers():
    assert two_sum([-3, 4, 3, 90], 0) == (0, 2)


def test_duplicates():
    assert two_sum([3, 3], 6) == (0, 1)


def test_large_input():
    nums = list(range(10_000))
    i, j = two_sum(nums, 19_997)
    assert nums[i] + nums[j] == 19_997
    assert i < j
