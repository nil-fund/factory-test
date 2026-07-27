from parity import is_odd


def test_is_odd_positive_odd():
    assert is_odd(3) is True


def test_is_odd_positive_even():
    assert is_odd(4) is False


def test_is_odd_zero():
    assert is_odd(0) is False
