from solution import my_atoi


def test_examples():
    assert my_atoi("42") == 42
    assert my_atoi("   -42") == -42
    assert my_atoi("4193 with words") == 4193
    assert my_atoi("words 987") == 0


def test_clamping():
    assert my_atoi("-91283472332") == -2147483648
    assert my_atoi("2147483648") == 2147483647


def test_sign_only_and_plus():
    assert my_atoi("+7") == 7
    assert my_atoi("-") == 0
