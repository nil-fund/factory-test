"""Tests for fibonacci module."""
from fibonacci import fibonacci


def test_fibonacci_0():
    """F(0) should return 0."""
    assert fibonacci(0) == 0, "F(0) should be 0"


def test_fibonacci_1():
    """F(1) should return 1."""
    assert fibonacci(1) == 1, "F(1) should be 1"


def test_fibonacci_2():
    """F(2) should return 1."""
    assert fibonacci(2) == 1, "F(2) should be 1"


def test_fibonacci_10():
    """F(10) should return 55."""
    assert fibonacci(10) == 55, "F(10) should be 55"


def test_fibonacci_20():
    """F(20) should return 6765."""
    assert fibonacci(20) == 6765, "F(20) should be 6765"


def test_fibonacci_negative_raises():
    """Negative input should raise ValueError."""
    try:
        fibonacci(-1)
        assert False, "Expected ValueError for negative input"
    except ValueError:
        pass  # Expected
