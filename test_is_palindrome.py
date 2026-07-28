from is_palindrome import is_palindrome


def test_is_palindrome_racecar():
    assert is_palindrome("racecar") is True


def test_is_palindrome_hello():
    assert is_palindrome("hello") is False


def test_is_palindrome_empty():
    assert is_palindrome("") is True


def test_is_palindrome_single_char():
    assert is_palindrome("a") is True


def test_is_palindrome_two_chars():
    assert is_palindrome("ab") is False


def test_is_palindrome_case_sensitive():
    assert is_palindrome("Aba") is False
