from fizzbuzz import fizzbuzz


def test_fizzbuzz_n1():
    assert fizzbuzz(1) == ["1"]


def test_fizzbuzz_n3():
    assert fizzbuzz(3) == ["1", "2", "Fizz"]


def test_fizzbuzz_n5():
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fizzbuzz_n15_includes_fizzbuzz_at_position_14():
    result = fizzbuzz(15)
    assert result[14] == "FizzBuzz"


def test_fizzbuzz_n15_full_sequence():
    assert fizzbuzz(15) == [
        "1", "2", "Fizz", "4", "Buzz",
        "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz",
    ]


def test_fizzbuzz_n0_empty():
    assert fizzbuzz(0) == []