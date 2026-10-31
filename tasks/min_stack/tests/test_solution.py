from solution import MinStack


def test_scenario():
    st = MinStack()
    st.push(-2)
    st.push(0)
    st.push(-3)
    assert st.get_min() == -3
    st.pop()
    assert st.top() == 0
    assert st.get_min() == -2


def test_duplicates():
    st = MinStack()
    st.push(2)
    st.push(2)
    st.push(1)
    assert st.get_min() == 1
    st.pop()
    st.pop()
    assert st.get_min() == 2
