"""Prime number operations used for just intonation."""

from functools import reduce
from math import gcd
from typing import List


def is_prime(number: int) -> bool:
    """States if a number is prime.

    Parameters:
        number: A number

    Returns:
        Whether or not the number is prime

    Examples:
        >>> is_prime(31)
        True

        >>> is_prime(42)
        False
    """
    for factor in range(2, number):
        if not number % factor:
            return False
    return True


def generate_primes(limit: int) -> List[int]:
    """Generates primes up to a given limit.

    Parameters:
        limit: The limit.

    Returns:
        Primes

    Examples:
        >>> generate_primes(31)
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    """
    return [n for n in range(2, limit + 1) if is_prime(n)]


def prime_factors(number: int) -> List[int]:
    """Finds prime factors of an integer (by trial-division).

    Parameters:
        number: The integer to factor

    Returns:
        Prime factors

    Examples:
        >>> prime_factors(314)
        [2, 157]

        >>> prime_factors(31)
        [31]
    """
    factor = 2
    factors = []
    while factor * factor <= number:
        if number % factor:
            factor += 1
        else:
            number //= factor
            factors.append(factor)
    if number > 1:
        factors.append(number)

    return factors


def lcm(numbers: List[int]) -> int:
    """Least common multiple of a list of integers.

    Parameters:
        numbers: List of integers

    Returns:
        Least common multiple

    Examples:
        >>> lcm([15, 3, 5])
        15

        >>> lcm([21, 6, 7])
        42
    """
    return reduce(lambda x, y: x * y // gcd(x, y), numbers)
