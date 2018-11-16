"""Prime number operations used for just intonation."""

from math import gcd
from functools import reduce


__version__ = '0.0.1'


def is_prime(number):
    """States if a number is prime.

    :param number: A number
    :type number: int

    :rtype: bool

    **Examples**

    >>> is_prime(31)
    True

    >>> is_prime(42)
    False
    """
    for factor in range(2, number):
        if not number % factor:
            return False
    return True


def generate_primes(limit):
    """Generates primes up to a given limit.

    :param limit: The limit.
    :type limit: int

    :rtype: list of int

    **Examples**

    >>> generate_primes(31)
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    """
    return [n for n in range(2, limit + 1) if is_prime(n)]


def prime_factors(number):
    """Finds prime factors of an integer (by trial-division).

    :param number: The integer to factor
    :type number: int

    :rtype: list of ints

    **Examples**

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


def lcm(numbers):
    """Least common multiple of a list of integers.

    :param numbers: List of integers
    :type numbers: list of int

    :rtype: int

    **Examples**

    >>> lcm([15, 3, 5])
    15

    >>> lcm([21, 6, 7])
    42
    """
    return reduce(lambda x, y: x * y // gcd(x, y), numbers)
