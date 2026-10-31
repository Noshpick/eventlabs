from solution import fizzbuzz_sum


def test_example():
    assert fizzbuzz_sum(10) == 33


def test_small():
    assert fizzbuzz_sum(1) == 0
    assert fizzbuzz_sum(3) == 3
    assert fizzbuzz_sum(15) == 60


def test_large_no_loop():
    # 3..999 divisible by 3 or 5: known Project Euler #1 answer for <1000
    assert fizzbuzz_sum(999) == 233168


def test_huge():
    assert fizzbuzz_sum(10**9) == 233333334166666668
