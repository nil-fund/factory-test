from is_prime import is_prime


def test_is_prime_zero():
    assert is_prime(0) is False


def test_is_prime_one():
    assert is_prime(1) is False


def test_is_prime_two():
    assert is_prime(2) is True


def test_is_prime_three():
    assert is_prime(3) is True


def test_is_prime_four():
    assert is_prime(4) is False


def test_is_prime_seventeen():
    assert is_prime(17) is True


def test_is_prime_hundred():
    assert is_prime(100) is False


def test_is_prime_negative():
    assert is_prime(-7) is False


def test_is_prime_large_prime():
    assert is_prime(7919) is True


def test_is_prime_large_composite():
    assert is_prime(8001) is False