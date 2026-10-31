from solution import group_anagrams


def norm(groups):
    return sorted(sorted(g) for g in groups)


def test_classic():
    got = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert norm(got) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]


def test_single_and_empty_str():
    assert norm(group_anagrams(["a"])) == [["a"]]
    assert norm(group_anagrams(["", ""])) == [["", ""]]
