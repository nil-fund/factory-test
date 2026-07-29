def count_vowels(s):
    """Return the count of vowels (a, e, i, o, u) in s, case-insensitive."""
    vowels = set("aeiou")
    return sum(1 for ch in s if ch.lower() in vowels)