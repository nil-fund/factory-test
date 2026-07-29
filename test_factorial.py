"""Tests for factorial module."""
from factorial import factorial


def test_factorial_0():
    """0! should return 1."""
    assert factorial(0) == 1, "0! should be 1"


def test_factorial_1():
    """1! should return 1."""
    assert factorial(1) == 1, "1! should be 1"


def test_factorial_5():
    """5! should return 120."""
    assert factorial(5) == 120, "5! should be 120"


def test_factorial_10():
    """10! should return 3628800."""
    assert factorial(10) == 3628800, "10! should be 3628800"


def test_factorial_negative_raises():
    """Negative input should raise ValueError."""
    try:
        factorial(-1)
        assert False, "Expected ValueError for negative input"
    except ValueError:
        pass  # Expected