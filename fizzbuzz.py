def fizzbuzz(n):
    """Return the fizzbuzz sequence for integers 1..n as a list of strings.

    Multiples of 3 -> 'Fizz', multiples of 5 -> 'Buzz',
    multiples of both 3 and 5 -> 'FizzBuzz', else the number as a string.
    """
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result