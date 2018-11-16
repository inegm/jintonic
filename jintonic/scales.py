"""Implements just intonation arbitrary and tetrachordal scales."""

from itertools import permutations, product

from .intervals import JustInterval
from .primes import is_prime


__version__ = '0.0.1'


class JustScale():
    """This class implements arbitrary just intonation scales."""

    def __init__(self, tones=None):
        """Initializes a JustScale.

        :param tones: A list of intervals or an object containing
            a list of intervals (that implements the attribute intervals)
        :type tones: list

        **Examples**

        >>> scale = JustScale([JustInterval(1, 1)])
        >>> scale.append(JustInterval(3, 2))
        >>> scale.append(JustInterval(2, 1))
        >>> scale
        JustScale([1/1, 3/2, 2/1])
        """
        self._tones = None
        self._pitch_mapping = None

        try:
            self.tones = tones.intervals
        except AttributeError:
            self.tones = tones

    def append(self, other):
        """Appends tones to the scale.

        :param other: A new tone
        :type other: JustInterval

        **Examples**

        >>> scale = JustScale([JustInterval(3, 2)])
        >>> scale.append(JustInterval(4, 3))
        >>> scale.tones
        [JustInterval(4, 3), JustInterval(3, 2)]
        """
        if not isinstance(other, JustInterval):
            msg = 'cannot append type {}. '.format(type(other))
            msg += 'Expecting type "JustInterval"'
            raise ValueError(msg)
        self._tones.append(other)

    def hertz(self, fundamental):
        """Translates scale intervals to pitches in Hertz over a fundamental

        .. note::

            Here, the fundamental is always 1/1 and is not to be mistaken with
            the first tone of the scale. If 1/1 is not part of the scale's
            tones, the fundamental will not be part of the scale.

        :param fundamental: The scale's 0 degree (fundamental) pitch in Hertz.
        :type fundamental: float
        """
        return [fundamental * tone for tone in self.tones]

    @property
    def tones(self):
        """JustScale tones.

        :param values: A list of tones
        :type values: list of JustInterval
        """
        return sorted(self._tones)

    @tones.setter
    def tones(self, values):
        """Sets JustScale tones."""
        for tone in values:
            if not isinstance(tone, JustInterval):
                msg = 'tones must be a list of JustIntervals. '
                msg += "Got '{}'".format(values)
                raise ValueError(msg)
        self._tones = values

    @property
    def intervals(self):
        """JustScale intervals.

        **Examples**

        >>> scale = JustScale([JustInterval(1, 1)])
        >>> scale.append(JustInterval(3, 2))
        >>> scale.append(JustInterval(2, 1))
        >>> scale.intervals
        [JustInterval(3, 2), JustInterval(4, 3)]
        """
        return [
            tone - self.tones[i-1]
            for i, tone in enumerate(self.tones)
        ][1:]

    @property
    def complement(self):
        """JustScale complement

        :rtype: JustScale

        **Examples**

        >>> scale = JustScale([JustInterval(1, 1)])
        >>> scale.append(JustInterval(3, 2))
        >>> scale.append(JustInterval(2, 1))
        >>> scale.complement
        JustScale([1/1, 4/3, 2/1])
        """
        tones = [tone.complement for tone in self.tones]
        return JustScale(tones)

    @property
    def prime_limit(self):
        """JustScale prime limit

        :rtype: int
        """
        return max([tone.prime_limit for tone in self.tones])

    @property
    def pitch_mapping(self):
        """Mapping of pitches to notation strings.

        :param values: A list, equal in length to the scale's list of
            intervals, containing lilypond string representations of the notes
            to be used in notation for each pitch.
        :type values: list of str
        """
        # TODO Default pitch mapper
        # Create a default pitch mapper. For example: if there are 8 pitches,
        # use the diatonic C representations. If 12, then use chromatic with
        # the lilpypond default for twelve-tone (all sharps ?). Otherwise,
        # keep the fifth and "perfect" intervals, then use accidentals. Etc.
        return self.pitch_mapping

    @pitch_mapping.setter
    def pitch_mapping(self, values):
        """Set a scale's pitch mapping."""
        if len(values) != self.tones:
            msg = 'length mismatch. Must map one to one with intervals.'
            raise ValueError(msg)
        for value in values:
            if not isinstance(value, str):
                # TODO Validate lilypond note values
                raise ValueError('invalid mapping.')

    def __repr__(self):
        """repr(self)"""
        pitches = ', '.join([
            '/'.join([str(tone.numerator), str(tone.denominator)])
            for tone in self.tones
        ])
        return "{}([{}])".format(self.__class__.__name__, pitches)


class JustTetrachord():
    """This class implements disjunct just intonation tetrachords."""

    def __init__(self, intervals=None, genus=None, prime_limit=7):
        """Initializes a JustTetrachord.

        A JustTetrachord can be constructed in one of two ways :

            - from a genus name (with naive division)
            - from a list of intervals between each successive tone

        :param intervals: A list of intervals
        :type intervals: :class:`justintonation.intervals.JustInterval`
        :param genus: One of 'enharmonic', 'chromatic', or 'diatonic'
        :type genus: str
        :param prime_limit: The prime limit to respect
        :type prime_limit: int

        **Examples**

        >>> JustTetrachord(genus='chromatic')
        JustTetrachord('chromatic' [27:28, 14:15, 5:6])

        >>> JustTetrachord(genus='enharmonic')
        JustTetrachord('enharmonic' [45:46, 23:24, 4:5])
        >>> JustTetrachord(genus='enharmonic').prime_limit
        23

        >>> intervals = []
        >>> intervals.append(JustInterval(32, 31))
        >>> intervals.append(JustInterval(31, 30))
        >>> intervals.append(JustInterval(5, 4))
        >>> JustTetrachord(intervals)
        JustTetrachord('enharmonic' [31:32, 30:31, 4:5])
        >>> JustTetrachord(intervals).prime_limit
        31
        """
        if not is_prime(prime_limit):
            msg = 'The prime limit must be a prime number. '
            msg += "Got: '{}'".format(prime_limit)
            raise ValueError(msg)
        self._prime_limit = prime_limit

        if intervals is not None:
            self.intervals = intervals
        elif genus is not None:
            self.genus = genus.strip().lower()
        else:
            self._intervals = []

    @classmethod
    def validate_tetrachord(cls, value):
        """Validates a tetrachord."""
        if len(value) != 3:
            msg = 'Tetrachords must be formed of exactly three intervals. '
            msg += 'Got: "{}"'.format(value)
            raise ValueError(msg)
        try:
            total_interval = sum(value)
        except TypeError:
            total_interval = sum(value.intervals)
        if total_interval != JustInterval(4, 3):
            msg = 'Tetrachord intervals must sum to JustInterval(4, 3). '
            msg += 'Got: "{}"'.format(sum(value))
            raise ValueError(msg)

    @property
    def intervals(self):
        """JustTetrachord intervals.

        :param value: A list of exactly three intervals which sum to 4:3
        :type value: list of JustInterval

        **Examples**

        >>> JustTetrachord(genus='enharmonic').intervals
        [JustInterval(46, 45), JustInterval(24, 23), JustInterval(5, 4)]
        """
        return self._intervals

    @intervals.setter
    def intervals(self, values):
        """Set JustTetrachord intervals."""
        self.validate_tetrachord(values)
        self._prime_limit = max(
            values[0].prime_limit,
            values[1].prime_limit,
            values[2].prime_limit
        )
        self._intervals = values

    @property
    def genus(self):
        """JustTetrachord genus.

        .. note::

            When setting the genus, the movable tone is set to its most basic
            position by dividing by two the interval remaining after taking the
            characteristic interval.

        :param value: A valid classical genus from ['enharmonic', 'chromatic',
            'diatonic']
        :type value: str
        """
        if not self.intervals:
            raise ValueError('Undefined intervals')
        end_intervals = [
            JustInterval(5, 4),
            JustInterval(6, 5),
            JustInterval(10, 9)
        ]
        genera = ['enharmonic', 'chromatic', 'diatonic']
        try:
            return genera[end_intervals.index(self.intervals[-1])]
        except ValueError:
            return 'non-classical'

    @genus.setter
    def genus(self, value):
        """Set JustTetrachord genus."""
        characteristic_intervals = {
            'enharmonic': JustInterval(5, 4),
            'chromatic': JustInterval(6, 5),
            'diatonic': JustInterval(10, 9)
        }
        characteristic = characteristic_intervals[value]
        remainder = JustInterval(4, 3) - characteristic
        intervals = remainder.divisions(2, self.prime_limit)
        intervals.append(characteristic)
        self.intervals = intervals

    @property
    def prime_limit(self):
        """JustTetrachord prime limit."""
        return self._prime_limit

    @property
    def permutations(self):
        """All (there are six) possible permutations of the JustTetrachord.

        :rtype: list of JustTetrachord
        """
        return [
            JustTetrachord(intervals=permutation)
            for permutation in permutations(self.intervals)
        ]

    def __repr__(self):
        """repr(self)"""
        return "{}('{}' [{}:{}, {}:{}, {}:{}])".format(
            self.__class__.__name__,
            self.genus,
            self.intervals[0].denominator,
            self.intervals[0].numerator,
            self.intervals[1].denominator,
            self.intervals[1].numerator,
            self.intervals[2].denominator,
            self.intervals[2].numerator
        )

    def __eq__(self, other):
        """self == other"""
        return self.intervals == other.intervals

    def __len__(self):
        """len(self)"""
        return len(self.intervals)


class JustTetrachordalScale():
    """This class implements disjunct just intonation tetrachordal scales."""

    def __init__(self, lower, upper=None):
        """Initializes a JustTetrachordalScale.

        :param lower: The lower tetrachord
        :type lower: JustTetrachord
        :param upper: The upper tetrachord. If None is passed, the lower
            tetrachord is also used for the upper, creating an 'equal'
            tetrachordal scale.
        :type upper: JustTetrachord

        **Examples**

        >>> JustTetrachordalScale(JustTetrachord(genus='enharmonic'))
         JustTetrachordalScale([46/45, 24/23, 5/4, 9/8, 46/45, 24/23, 5/4])
        """
        self._lower = None
        self._upper = None

        self.lower = lower
        if upper is None:
            self.upper = lower
        else:
            self.upper = upper

    @property
    def lower(self):
        """Lower JustTetrachord.

        :param value: JustTetrachord
        """
        return self._lower

    @lower.setter
    def lower(self, value):
        """Set lower JustTetrachord."""
        JustTetrachord.validate_tetrachord(value)
        self._lower = value

    @property
    def upper(self):
        """Upper JustTetrachord.

        :param value: JustTetrachord
        """
        return self._upper

    @upper.setter
    def upper(self, value):
        """Set upper JustTetrachord."""
        JustTetrachord.validate_tetrachord(value)
        self._upper = value

    @property
    def intervals(self):
        """JustTetrachordalScale intervals.

        **Examples**

        >>> JustTetrachordalScale(JustTetrachord(genus='diatonic')).intervals
        [JustInterval(16, 15), JustInterval(9, 8), JustInterval(10, 9),
        JustInterval(9, 8), JustInterval(16, 15), JustInterval(9, 8),
        JustInterval(10, 9)]
        """
        return (
            self.lower.intervals +
            [JustInterval(9, 8)] +
            self.upper.intervals
        )

    @property
    def complement(self):
        """JustTetrachordalScale complement

        :rtype: JustScale

        .. note::

            Returns a JustScale ! The result will not be Tetrachordal.

        **Examples**

        >>> JustTetrachordalScale(JustTetrachord(genus='chromatic')).complement
        JustScale([1/1, 6/5, 9/7, 4/3, 3/2, 9/5, 27/14, 2/1])
        """
        tones = [tone.complement for tone in self.tones]
        return JustScale(tones)

    @property
    def tones(self):
        """JustTetrachordalScale tones.

        >>> JustTetrachordalScale(JustTetrachord(genus='diatonic')).tones
        [JustInterval(1, 1), JustInterval(16, 15), JustInterval(6, 5),
        JustInterval(4, 3), JustInterval(3, 2), JustInterval(8, 5),
        JustInterval(9, 5), JustInterval(2, 1)]
        """
        tones = [JustInterval(1, 1)]
        tones += [
            JustInterval(1, 1) + sum(self.intervals[:i])
            for i in range(1, len(self.intervals))]
        tones += [JustInterval(2, 1)]
        return tones

    def hertz(self, fundamental):
        """Translates scale intervals to pitches in Hertz over a fundamental

        :param fundamental: The scale's 0 degree (fundamental) pitch in Hertz.
        :type fundamental: float

        :rtype: list of float

        **Examples**

        >>> JustTetrachordalScale(JustTetrachord(genus='diatonic')).hertz(60.)
        [60.0, 64.0, 72.0, 80.0, 90.0, 96.0, 108.0, 120.0]
        """
        return [fundamental * tone for tone in self.tones]

    @property
    def genera(self):
        """JustTetrachordalScale genera for each constituent tetrachord.

        :rtype: tuple

        **Examples**

        >>> intervals = []
        >>> intervals.append(JustInterval(32, 31))
        >>> intervals.append(JustInterval(31, 30))
        >>> intervals.append(JustInterval(5, 4))
        >>> scale = JustTetrachordalScale(JustTetrachord(intervals))
        >>> scale.upper = JustTetrachord(genus='diatonic')
        >>> scale.genera
        ('enharmonic', 'diatonic')
        """
        return (self.lower.genus, self.upper.genus)

    @property
    def is_equal(self):
        """Evaluates whether the JustTetrachordalScale is equal or mixed."""
        return self.lower == self.upper

    @property
    def prime_limit(self):
        """JustTetrachordalScale prime limit."""
        return max(self.lower.prime_limit, self.upper.prime_limit)

    @property
    def permutations(self):
        """All (thirty-six) possible permutations of the JustTetrachordalScale.

        :rtype: list of JustTetrachordalScale
        """
        return [
            JustTetrachordalScale(pair[0], pair[1])
            for pair in product(
                self.lower.permutations,
                self.upper.permutations
            )
        ]

    @property
    def pitch_mapping(self):
        """Mapping of pitches to notation strings.

        :param values: A list, equal in length to the scale's list of
            intervals, containing lilypond string representations of the notes
            to be used in notation for each pitch.
        :type values: list of str
        """
        # TODO Default pitch mapper
        # Create a default pitch mapper. For example: if there are 8 pitches,
        # use the diatonic C representations. If 12, then use chromatic with
        # the lilpypond default for twelve-tone (all sharps ?). Otherwise,
        # keep the fifth and "perfect" intervals, then use accidentals. Etc.
        return self.pitch_mapping

    @pitch_mapping.setter
    def pitch_mapping(self, values):
        """Set a scale's pitch mapping."""
        if len(values) != self.tones:
            msg = 'length mismatch. Must map one to one with intervals.'
            raise ValueError(msg)
        for value in values:
            if not isinstance(value, str):
                # TODO Validate lilypond note values
                raise ValueError('invalid mapping.')

    def __repr__(self):
        """repr(self)"""
        pitches = ', '.join([
            '/'.join([str(interval.numerator), str(interval.denominator)])
            for interval in self.intervals
        ])
        return "{}([{}])".format(self.__class__.__name__, pitches)
