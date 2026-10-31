from solution import is_palindrome


def test_classic():
    assert is_palindrome("A man, a plan, a canal: Panama") is True


def test_not_palindrome():
    assert is_palindrome("race a car") is False


def test_empty():
    assert is_palindrome("") is True


def test_digits_and_case():
    assert is_palindrome("No 'x' in Nixon") is True
    assert is_palindrome("12321") is True
    assert is_palindrome("1231") is False
