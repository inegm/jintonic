"""Implements the just intonation lattice."""

from .primes import is_prime, generate_primes
from .intervals import JustInterval, primary_interval

__version__ = '0.0.1'


class JustLattice():
    """This class implements just intonation lattices."""

    def __init__(self, fundamental=None, prime_limit=7):
        """Initializes a JustLattice.

        :param prime_limit: The prime limit. A prime number.
        :type prime_limit: int
        :param fundamental: The 1/1 pitch in Hertz
        :type fundamental: float

        **Examples**

        >>> JustLattice(60)
        JustLattice(60.0 - 1/1 (60.0))
        """
        self._prime_limit = None
        self.prime_limit = prime_limit

        self._fundamental = None
        self._pitch = None
        self._cents = None
        self._tone = JustInterval(1, 1)
        self._node = (0, 0, 0)
        self._path = [self._node]

        if fundamental is not None:
            self.fundamental = fundamental

    def traverse(self, *vector):
        """Traverses a just intonation lattice.

        :param vector: Number of steps along each axis. Steps are assigned to
            an axis based on position. The first argument is on the three-limit
            axis, the second on the five-limit, third on the seven-limit,
            etc. To stay in place on an axis, pass 0 for that axis.
        :type arg: tuple of int

        **Examples**

        >>> lattice = JustLattice(60)
        >>> lattice.traverse(1, 0, 0)
        JustLattice(60.0 - 3/2 (90.0))
        >>> lattice.traverse(-2, 0, 0)
        JustLattice(60.0 - 4/3 (80.0))
        >>> lattice.traverse(1, 1, 0)
        JustLattice(60.0 - 5/4 (75.0))
        >>> lattice.traverse(0, -2, 0)
        JustLattice(60.0 - 8/5 (96.0))
        >>> lattice.traverse(0, 1, 1)
        JustLattice(60.0 - 7/4 (105.0))
        >>> lattice.traverse(0, 0, -2)
        JustLattice(60.0 - 8/7 (68.5714))
        >>> lattice.traverse(2, 0, 1)
        JustLattice(60.0 - 9/8 (67.5))
        >>> lattice.traverse(-4, 0, 0)
        JustLattice(60.0 - 16/9 (106.6667))
        """
        primary_intervals = [
            primary_interval(prime)
            for prime in generate_primes(self.prime_limit)[1:]
        ]
        if len(vector) > len(primary_intervals):
            return NotImplemented

        for axis, steps in enumerate(list(vector)):
            interval = primary_intervals[axis]**abs(steps)
            if steps > 0:
                self._tone += interval
            elif steps < 0:
                self._tone -= interval
            else:
                continue

        self._tone = self._tone.base_octave
        self._node = vector
        self._path.append(vector)

        return self

    def undo(self, steps=1):
        """Undo a traversal.

        :param steps: Number of steps to undo
        :type steps: int

        **Examples**

        >>> lattice = JustLattice(60)
        >>> lattice.traverse(1, 0, 0)
        JustLattice(60.0 - 3/2 (90.0))
        >>> lattice.undo(1)
        JustLattice(60.0 - 1/1 (60.0))
        """
        for _ in range(steps):
            vector = self._path.pop()
            self.traverse(*(-1 * distance for distance in vector))

        return self

    def to_fundamental(self):
        """Return to 1/1 without losing path history.

        **Examples**

        >>> lattice = JustLattice(60)
        >>> lattice.traverse(1, 0, 0)
        JustLattice(60.0 - 3/2 (90.0))
        >>> lattice.to_fundamental()
        JustLattice(60.0 - 1/1 (60.0))
        """
        axes = len(self._node)
        root_node = (0, ) * axes
        self._node = root_node
        self._tone = JustInterval(1, 1)
        self._path.append(root_node)
        self._pitch = self._fundamental

        return self

    def reset_path(self):
        """Clear path history and return to 1/1."""
        self.to_fundamental()
        axes = len(self._node)
        root_node = (0, ) * axes
        self._path = root_node

        return self

    def to_node(self, *node):
        """Traverse to a specific node.

        **Examples**

        >>> lattice = JustLattice(60)
        >>> lattice.traverse(1, 0, 0)
        JustLattice(60.0 - 3/2 (90.0))
        >>> lattice.to_node(0, 0, 0)
        JustLattice(60.0 - 1/1 (60.0))
        """
        self.to_fundamental()
        self.traverse(*node)

        return self

    @property
    def prime_limit(self):
        """The prime limit.

        :param value: A prime number.
        :type value: int

        **Examples**

        >>> JustLattice(60).prime_limit
        7
        """
        return self._prime_limit

    @prime_limit.setter
    def prime_limit(self, value):
        """Sets the prime limit."""
        if not is_prime(value):
            msg = 'Prime limit must be a prime number. '
            msg += "Got '{}'".format(value)
        self._prime_limit = value

    @property
    def fundamental(self):
        """Fundamental (1/1) pitch in Hertz.

        :param value: Fundamental (1/1) pitch in Hertz
        :type value: float

        **Examples**

        >>> JustLattice(60).fundamental
        60.0
        """
        return self._fundamental

    @fundamental.setter
    def fundamental(self, value):
        """Set the fundamental (1/1) pitch in Hertz."""
        try:
            self._fundamental = float(value)
            self._pitch = self._fundamental * self._tone
        except ValueError:
            msg = "Fundamental must be numeric. Got '{}'.".format(
                type(value))
            raise ValueError(msg)

    @property
    def hertz(self):
        """Current node's pitch in Hertz.

        **Examples**

        >>> lattice = JustLattice(60)
        >>> lattice.traverse(1, 0, 0).hertz
        90.0
        """
        return self._fundamental * self._tone

    @property
    def cents(self):
        """Current node's interval in Cents.

        **Examples**

        >>> lattice = JustLattice(60)
        >>> round(lattice.traverse(1, 0, 0).cents, 3)
        701.955
        """
        return self._tone.cents

    @property
    def tone(self):
        """Current node's tone.

        **Examples**

        >>> lattice = JustLattice(60)
        >>> lattice.traverse(1, 0, 0).tone
        JustInterval(3, 2)
        """
        return self._tone

    @property
    def node(self):
        """Current node as a tuple with length equivalent to number of axes.

        **Examples**

        >>> lattice = JustLattice(60)
        >>> lattice.traverse(0, 2, 3).node
        (0, 2, 3)
        """
        return self._node

    @property
    def path(self):
        """Current traversal history.

        **Examples**

        >>> lattice = JustLattice(60)
        >>> lattice.traverse(0, 2, 3).path
        [(0, 0, 0), (0, 2, 3)]
        """
        return self._path

    def __repr__(self):
        """repr(self)"""
        return '{}({} - {}/{} ({}))'.format(
            self.__class__.__name__,
            self.fundamental,
            self.tone.numerator,
            self.tone.denominator,
            round(self.hertz, 4)
        )
