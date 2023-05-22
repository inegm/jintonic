"""Implements just intonation intervals (ratios)."""
from __future__ import annotations

import operator
import re
from copy import deepcopy
from math import gcd, log
from typing import Any, Callable, List, Tuple

from .primes import is_prime, prime_factors

# String format for just ratios (JustInterval). eg: '3:2'
_RATIO_FORMAT = re.compile(
    r"""
    \A\s*
    (?P<num>\d*):(?P<denom>\d*)
    \s*\Z
""",
    re.VERBOSE | re.IGNORECASE,
)


def primary_interval(
    prime_limit: int,
    sub_harmonic: bool = False,
    max_pot_exp: int = 500,
) -> JustInterval:
    """Returns the primary interval for a given prime limit.

    Parameters:
        prime_limit: A prime number
        sub_harmonic: Whether the primary interval is a harmonic primary
            (the default) or a sub-harmonic primary.
        max_pot_exp: Maximum power of two exponent to limit iterations

    Examples:
        >>> primary_interval(7)
        JustInterval(7, 4)

        >>> primary_interval(19)
        JustInterval(19, 16)

        >>> primary_interval(3, sub_harmonic=True)
        JustInterval(4, 3)
    """
    pot = 2
    exp = 2
    max_pot = 2**max_pot_exp
    while (pot**exp < prime_limit) and (pot < max_pot):
        exp += 1
    pot = pot ** (exp - 1)
    if sub_harmonic:
        return JustInterval(prime_limit, pot).complement
    return JustInterval(prime_limit, pot)


class JustInterval:
    """This class implements just intonation intervals."""

    def __init__(self, numerator: int, denominator: int):
        """Initializes a JustInterval.

        Parameters:
            numerator: Numerator
            denominator: Denominator

        Examples:
            >>> JustInterval(4, 3)
            JustInterval(4, 3)
        """
        if not (isinstance(numerator, int) and isinstance(denominator, int)):
            msg = "Both components must be integers. "
            msg += "Got numerator: {}, denominator: {}".format(
                type(numerator), type(denominator)
            )
            raise TypeError(msg)

        if denominator > numerator:
            msg = "Numerator must be greater than or equal to denominator. "
            msg += "Got numerator: {}, denominator: {}".format(numerator, denominator)
            raise ValueError(msg)

        if denominator == 0:
            raise ZeroDivisionError("JustRatio({}, 0)".format(numerator))

        if denominator < 1:
            msg = "Denominator must be greater than 0. "
            msg += "Got: {}".format(numerator)
            raise ValueError(msg)

        common = gcd(numerator, denominator)
        numerator //= common
        denominator //= common

        self._numerator = numerator
        self._denominator = denominator

    @classmethod
    def from_string(cls, interval: str) -> JustInterval:
        """Creates a JustInterval from a string representation.

        Parameters:
            interval: A string representation of an interval in the
                `numerator:denominator` format.

        Returns:
            A JustInterval

        Examples:
            >>> JustInterval.from_string('3:2')
            JustInterval(3, 2)

            >>> JustInterval.from_string('3:3')
            JustInterval(1, 1)

            >>> JustInterval.from_string('6:3')
            JustInterval(2, 1)
        """
        re_match = _RATIO_FORMAT.match(interval)
        if re_match is None:
            msg = "Invalid literal for JustRatio: {}".format(interval)
            raise ValueError(msg)
        try:
            numerator = int(re_match.group("num"))
            denominator = int(re_match.group("denom"))
            return JustInterval(numerator=numerator, denominator=denominator)
        except ValueError:
            msg = "Invalid literal for JustRatio: {}".format(interval)
            raise ValueError(msg)

    @classmethod
    def from_two_hertz(cls, apitch: float, bpitch: float) -> JustInterval:
        """Creates a JustInterval from two Hertz values.

        Parameters:
            apitch: A value in Hertz (which will be truncated to an int)
            bpitch: A value in Hertz (which will be truncated to an int)

        Returns:
            A JustInterval

        Examples:
            >>> JustInterval.from_two_hertz(220, 440)
            JustInterval(2, 1)
        """
        smaller = apitch if apitch <= bpitch else bpitch
        greater = apitch if apitch > bpitch else bpitch

        return cls(int(greater), int(smaller))

    def divisions(
        self,
        divisor: int,
        prime_limit: int = 7,
        max_iterations: int = 30,
    ) -> List[JustInterval]:
        """Divides a just interval into intervals that respect a prime limit.

        Parameters:
            divisor: Number of divisions.
            prime_limit: The prime limit, a prime number.
            max_iterations: A limit to how many divisions this method will
                try before giving up on dividing within the prime limit.

        Returns:
            The resulting JustIntervals

        Examples:
            >>> JustInterval(2, 1).divisions(4, 5)
            [JustInterval(10, 9), JustInterval(9, 8), JustInterval(6, 5),
            JustInterval(4, 3)]

            >>> JustInterval(16, 15).divisions(2, 31)
            [JustInterval(32, 31), JustInterval(31, 30)]
        """
        if not is_prime(prime_limit):
            msg = "The prime limit must be a prime number. "
            msg += "Got: '{}'".format(prime_limit)
            raise ValueError(msg)

        factor = divisor
        divisions: List[JustInterval] = []
        divrange: List[int] = []
        i = 0
        while i <= max_iterations:
            num = self.numerator * factor
            denom = self.denominator * factor

            divrange = list(range(denom, num + 1))
            primes: List[int] = []
            for number in divrange:
                if is_prime(number) and (number > prime_limit):
                    primes.append(number)
            for prime in primes:
                divrange.remove(prime)
            if len(divrange) != divisor + 1:
                factor += 1
                i += 1
                continue
            else:
                break

        divrange.reverse()
        for j, number in enumerate(divrange):
            try:
                divisions.append(JustInterval(number, divrange[j + 1]))
            except IndexError:
                continue

        return sorted(divisions)

    @property
    def numerator(self) -> int:
        """JustInterval numerator."""
        return self._numerator

    @property
    def denominator(self) -> int:
        """JustInterval denominator."""
        return self._denominator

    @property
    def prime_limit(self) -> int:
        """JustInterval prime limit.

        Examples:
            >>> JustInterval(64, 49).prime_limit
            7
        """
        if self.base_octave == JustInterval(1, 1):
            return 1
        num = max(prime_factors(self.numerator))
        denom = max(prime_factors(self.denominator))

        return max(num, denom)

    @property
    def is_superparticular(self) -> bool:
        """Superparticular just intervals are of the form x+1:x

        Examples:
            >>> JustInterval(3, 2).is_superparticular
            True
        """
        return self.numerator == self.denominator + 1

    @property
    def base_octave(self) -> JustInterval:
        """The interval within the range 1:1 to 2:1

        Examples:
            >>> JustInterval.from_string('9:4').base_octave
            JustInterval(9, 8)
        """
        cself = deepcopy(self)
        while cself >= JustInterval(2, 1):
            cself -= JustInterval(2, 1)
        return cself

    @property
    def complement(self) -> JustInterval:
        """JustInterval complement.

        The interval which, when added to this interval, yields an
        octave. This only applies to intervals smaller than the octave and
        will return `NotImplemented` if self is an interval larger than an
        octave.

        Returns:
            The interval's complement

        Note:
            Returns a copy

        Examples:
            >>> JustInterval(3, 2).complement
            JustInterval(4, 3)
        """
        octave = JustInterval(2, 1)
        if self < octave:
            return octave - self
        if self == octave:
            return JustInterval(1, 1)
        return NotImplemented

    @property
    def cents(self) -> float:
        """JustInterval expressed in Cents.

        Returns:
            The interval in Cents

        Examples:
            >>> round(JustInterval(3, 2).cents, 3)
            701.955
        """
        return log(self.numerator / self.denominator, 10) * (1200 / log(2, 10))

    def _prepare_division(self, number: int) -> Tuple[int, int]:
        """Helper for JustInterval division."""
        if not isinstance(number, int):
            msg = "Must be int, not {}".format(type(number))
            raise TypeError(msg)

        if not self.is_superparticular:
            if number % (self.numerator - self.denominator):
                msg = "{} is not divisible by {}".format(self, number)
                raise ValueError(msg)
            factor = number // (self.numerator - self.denominator)
            num = self.numerator * factor
            denom = self.denominator * factor

        else:
            num = self.numerator * number
            denom = self.denominator * number

        return num, denom

    def __repr__(self):
        """repr(self)"""
        return "{}({}, {})".format(
            self.__class__.__name__, self._numerator, self.denominator
        )

    def __add__(self, other: JustInterval) -> JustInterval:
        """JustInterval addition.

        Examples:

        >>> JustInterval(3, 2) + JustInterval(4, 3)
        JustInterval(2, 1)
        """
        if not isinstance(other, JustInterval):
            other = JustInterval(other.numerator, other.denominator)
        return JustInterval(
            self.numerator * other.numerator, self.denominator * other.denominator
        )

    def __radd__(self, other: JustInterval) -> JustInterval:
        """JustInterval right of operator addition.

        Examples:

        >>> sum((JustInterval(3, 2), JustInterval(4, 3)))
        JustInterval(2, 1)
        """
        if other == 0:
            other = JustInterval(1, 1)
        return self + other

    def __sub__(self, other: JustInterval) -> JustInterval:
        """JustInterval substraction.

        Examples:

        >>> JustInterval(3, 2) - JustInterval(9, 8)
        JustInterval(4, 3)
        >>> JustInterval(1, 1) - JustInterval(3, 2)
        JustInterval(4, 3)
        """
        if other > self:
            cself = deepcopy(self)
            cself += JustInterval(2, 1)
            return cself - other
        return JustInterval(
            self.numerator * other.denominator, self.denominator * other.numerator
        )

    def __mul__(self, other):
        """JustInterval left of operator multiplication."""
        return NotImplemented

    def __rmul__(self, other: float) -> float:
        """JustInterval right of operator multiplication.

        This is used to calculate the absolute frequency of a pitch _this_
        interval above it.

        Examples:

        >>> 440 * JustInterval(3, 2)
        660.0
        """
        try:
            return other * (self.numerator / self.denominator)
        except TypeError:
            msg = "Can't multiply sequence by non-int of type '{}'".format(
                self.__class__.__name__
            )
            raise TypeError(msg)

    def __pow__(self, other: int) -> JustInterval:
        """JustInterval raised to a power. Used for chaining an interval.

        Examples:

        >>> JustInterval(3, 2) ** 3
        JustInterval(27, 8)
        """
        if other < 0:
            msg = "JustInterval can only be raised to positive powers. "
            msg += "Got '{}'".format(other)
            raise ValueError(msg)
        elif other == 0:
            return JustInterval(1, 1)
        return sum([self] * other)  # type: ignore

    def __truediv__(self, other: int) -> List[JustInterval]:
        """Naive JustInterval division.

        For divisions within a given prime limit, use self.divisions()

        :rtype: JustInterval

        Examples:

        >>> JustInterval(2, 1) / 2
        [JustInterval(4, 3), JustInterval(3, 2)]
        >>> JustInterval(2, 1) / 3
        [JustInterval(6, 5), JustInterval(5, 4), JustInterval(4, 3)]
        >>> JustInterval(7, 4) / 3
        [JustInterval(7, 6), JustInterval(6, 5), JustInterval(5, 4)]
        """
        num, denom = self._prepare_division(other)

        return sorted([JustInterval(n, n - 1) for n in range(denom + 1, num + 1)])

    def __rtruediv__(self, other):
        """There's no sense dividing something by a JustInterval."""
        return NotImplemented

    def _richcmp(self, other: JustInterval, oper: Callable) -> bool:
        """Helper for comparison operators, for internal use only."""
        return oper(
            self.numerator / self.denominator, other.numerator / other.denominator
        )

    def __eq__(self, other: Any) -> bool:
        """self == other"""
        if not isinstance(other, JustInterval):
            return False
        return self._richcmp(other, operator.eq)

    def __lt__(self, other: JustInterval) -> bool:
        """self < other"""
        return self._richcmp(other, operator.lt)

    def __gt__(self, other: JustInterval) -> bool:
        """self > other"""
        return self._richcmp(other, operator.gt)

    def __le__(self, other: JustInterval) -> bool:
        """self <= other"""
        return self._richcmp(other, operator.le)

    def __ge__(self, other: JustInterval) -> bool:
        """self >= other"""
        return self._richcmp(other, operator.ge)

    def __bool__(self) -> bool:
        """self != 0"""
        return self._numerator != 0
