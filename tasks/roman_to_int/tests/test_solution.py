from solution import roman_to_int


def test_examples():
    assert roman_to_int("III") == 3
    assert roman_to_int("LVIII") == 58
    assert roman_to_int("MCMXCIV") == 1994


def test_subtractive():
    assert roman_to_int("IX") == 9
    assert roman_to_int("CDXLIV") == 444
