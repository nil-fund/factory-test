def factorial(n):
    """Return n! (n factorial) for non-negative integers.

    Args:
        n: Non-negative integer

    Returns:
        int: n factorial (0!=1, 1!=1, 5!=120, ...)

    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result