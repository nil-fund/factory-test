from is_even import is_even


def test_is_even_zero():
    assert is_even(0) is True


def test_is_even_one():
    assert is_even(1) is False


def test_is_even_two():
    assert is_even(2) is True


def test_is_even_negative_even():
    assert is_even(-2) is True


def test_is_even_negative_odd():
    assert is_even(-1) is False


def test_is_even_large_even():
    assert is_even(1000000) is True
