def fibonacci(n):
    """Return the nth Fibonacci number (0-indexed).
    
    Args:
        n: Non-negative integer index
        
    Returns:
        int: The nth Fibonacci number (F(0)=0, F(1)=1, F(2)=1, ...)
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    # Iterative approach for efficiency
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
