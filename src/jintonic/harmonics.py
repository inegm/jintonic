"""Tools for dealing with harmonic series."""
from __future__ import annotations

from functools import reduce
from math import gcd
from typing import List

from .intervals import JustInterval
from .primes import lcm, prime_factors


def tones_to_harmonic_segment(
    tones: List[JustInterval],
    sub: bool = False,
) -> List[int]:
    """Converts a series of tones to a harmonic or sub-harmonic segment.

    :param tones: A series of tones.
    :param sub: When True, returns a sub-harmonic segment. Else, a harmonic
        (overtone) segment.

    **Examples**

    >>> from .intervals import JustInterval
    >>> tones = []
    >>> tones.append(JustInterval(16, 15))
    >>> tones.append(JustInterval(4, 3))
    >>> tones.append(JustInterval(8, 5))
    >>> tones_to_harmonic_segment(tones)
    [4, 5, 6]

    >>> tones = []
    >>> tones.append(JustInterval(9, 5))
    >>> tones.append(JustInterval(9, 8))
    >>> tones.append(JustInterval(27, 20))
    >>> tones.append(JustInterval(63, 40))
    >>> tones_to_harmonic_segment(tones)
    [4, 5, 6, 7]

    TODO I'm not convinced this example (from p. 29) is correct, give an example
    of a subharmonic segment that works.

    >> tones = []
    >> tones.append(JustInterval(21, 20))
    >> tones.append(JustInterval(6, 5))
    >> tones.append(JustInterval(7, 6))
    >> tones_to_harmonic_segment(tones, sub=True)
    [8, 7, 6]
    """
    if sub:
        _tones = [(tone.denominator, tone.numerator) for tone in tones]
    else:
        _tones = [(tone.numerator, tone.denominator) for tone in tones]

    lcm_tones = lcm([tone[1] for tone in _tones])
    # print(lcm_tones)
    segment = [tone[0] * (lcm_tones // tone[1]) for tone in _tones]
    # print(segment)
    gcd_segment = reduce(gcd, segment)
    segment = [harmonic // gcd_segment for harmonic in segment]
    if sub:
        segment.reverse()
    for i, harmonic in enumerate(segment):
        try:
            if harmonic / 2 == segment[i + 1] - 1:
                segment[i] = harmonic // 2
        except IndexError:
            continue
    if sub:
        segment.reverse()
    return segment


def harmonic_to_identity(harmonic: int) -> int:
    """Converts a harmonic number to its tone identity.

    :param harmonic: A harmonic number

    **Examples**

    >>> harmonic_to_identity(6)
    3
    """
    return harmonic // (2 ** (prime_factors(harmonic).count(2)))


def harmonic_segment_to_identities(segment: List[int]) -> List[int]:
    """Converts a harmonic or sub-harmonic segment to its tone identities.

    :param segment: A harmonic, or sub-harmonic, segment

    **Examples**

    >>> harmonic_segment_to_identities([4, 5, 6])
    [1, 5, 3]

    >>> harmonic_segment_to_identities([10, 12, 15])
    [5, 3, 15]

    >>> harmonic_segment_to_identities([4, 5, 6, 7, 9])
    [1, 5, 3, 7, 9]
    """
    return [harmonic_to_identity(harmonic) for harmonic in segment]
