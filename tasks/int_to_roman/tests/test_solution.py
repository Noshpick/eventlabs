from solution import int_to_roman


def test_examples():
    assert int_to_roman(3) == "III"
    assert int_to_roman(58) == "LVIII"
    assert int_to_roman(1994) == "MCMXCIV"


def test_subtractive_and_large():
    assert int_to_roman(9) == "IX"
    assert int_to_roman(444) == "CDXLIV"
    assert int_to_roman(3749) == "MMMDCCXLIX"
