from solution import reverse_words


def test_basic():
    assert reverse_words("hello world") == "world hello"


def test_extra_spaces():
    assert reverse_words("  a  b  ") == "b a"
    assert reverse_words("the   sky is blue") == "blue is sky the"


def test_edge_cases():
    assert reverse_words("") == ""
    assert reverse_words("single") == "single"
