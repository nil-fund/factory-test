from count_vowels import count_vowels


def test_count_vowels_hello():
    assert count_vowels("hello") == 2


def test_count_vowels_uppercase():
    assert count_vowels("AEIOU") == 5


def test_count_vowels_empty():
    assert count_vowels("") == 0


def test_count_vowels_no_vowels():
    assert count_vowels("xyz") == 0


def test_count_vowels_mixed_case():
    assert count_vowels("aAeEiIoOuU") == 10


def test_count_vowels_no_vowels_consonants():
    assert count_vowels("rhythm") == 0