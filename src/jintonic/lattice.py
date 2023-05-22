"""Implements the just intonation lattice."""
from __future__ import annotations

from typing import List

from .intervals import JustInterval, primary_interval
from .primes import generate_primes, is_prime


class JustLattice:
    """This class implements just intonation lattices."""

    def __init__(self, fundamental: float, prime_limit: int = 7):
        """Initializes a JustLattice.

        Parameters:
            prime_limit: The prime limit. A prime number.
            fundamental: The 1/1 pitch in Hertz

        Examples:
            >>> JustLattice(60)
            JustLattice(60.0 Hz, 1/1, 60.0 Hz)
        """
        self._fundamental: float = float(fundamental)
        self._prime_limit: int = prime_limit

        self._tone: JustInterval = JustInterval(1, 1)
        self._node: List[int] = [0, 0, 0]
        self._path: List[List[int]] = [self._node]

    def traverse(self, vector: List[int]):
        """Traverses a just intonation lattice.

        Parameters:
            vector: Number of steps along each axis. Steps are assigned to
                an axis based on position. The first argument is on the three-limit
                axis, the second on the five-limit, third on the seven-limit,
                etc. To stay in place on an axis, pass 0 for that axis.

        Examples:
            >>> lattice = JustLattice(60)
            >>> lattice.traverse([1, 0, 0])
            JustLattice(60.0 Hz, 3/2, 90.0 Hz)
            >>> lattice.traverse([-2, 0, 0])
            JustLattice(60.0 Hz, 4/3, 80.0 Hz)
            >>> lattice.traverse([1, 1, 0])
            JustLattice(60.0 Hz, 5/4, 75.0 Hz)
            >>> lattice.traverse([0, -2, 0])
            JustLattice(60.0 Hz, 8/5, 96.0 Hz)
            >>> lattice.traverse([0, 1, 1])
            JustLattice(60.0 Hz, 7/4, 105.0 Hz)
            >>> lattice.traverse([0, 0, -2])
            JustLattice(60.0 Hz, 8/7, 68.5714 Hz)
            >>> lattice.traverse([2, 0, 1])
            JustLattice(60.0 Hz, 9/8, 67.5 Hz)
            >>> lattice.traverse([-4, 0, 0])
            JustLattice(60.0 Hz, 16/9, 106.6667 Hz)
        """
        primary_intervals = [
            primary_interval(prime) for prime in generate_primes(self.prime_limit)[1:]
        ]
        if len(vector) > len(primary_intervals):
            return NotImplemented

        for axis, steps in enumerate(list(vector)):
            interval = primary_intervals[axis] ** abs(steps)
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

    def undo(self, steps: int = 1):
        """Undo a traversal.

        Parameters:
            steps: Number of steps to undo

        Examples:
            >>> lattice = JustLattice(60)
            >>> lattice.traverse([1, 0, 0])
            JustLattice(60.0 Hz, 3/2, 90.0 Hz)
            >>> lattice.undo(1)
            JustLattice(60.0 Hz, 1/1, 60.0 Hz)
        """
        for _ in range(steps):
            vector = self._path.pop()
            self.traverse([-1 * distance for distance in vector])

        return self

    def to_fundamental(self):
        """Return to 1/1 without losing path history.

        Examples:
            >>> lattice = JustLattice(60)
            >>> lattice.traverse([1, 0, 0])
            JustLattice(60.0 Hz, 3/2, 90.0 Hz)
            >>> lattice.to_fundamental()
            JustLattice(60.0 Hz, 1/1, 60.0 Hz)
        """
        axes = len(self._node)
        root_node = [0] * axes
        self._node = root_node
        self._tone = JustInterval(1, 1)
        self._path.append(root_node)
        self._pitch = self._fundamental

        return self

    def reset_path(self):
        """Clear path history and return to 1/1."""
        self.to_fundamental()
        axes = len(self._node)
        root_node = [0] * axes
        self._path = [root_node]

        return self

    def to_node(self, node: List[int]):
        """Traverse to a specific node.

        Examples:
            >>> lattice = JustLattice(60)
            >>> lattice.traverse([1, 0, 0])
            JustLattice(60.0 Hz, 3/2, 90.0 Hz)
            >>> lattice.to_node([0, 0, 0])
            JustLattice(60.0 Hz, 1/1, 60.0 Hz)
        """
        self.to_fundamental()
        self.traverse(node)

        return self

    @property
    def prime_limit(self) -> int:
        """The prime limit.

        Returns:
            The prime limit of the lattice

        Examples:
            >>> JustLattice(60).prime_limit
            7
        """
        return self._prime_limit

    @prime_limit.setter
    def prime_limit(self, value: int):
        """The prime limit.

        Parameters:
            value: A prime number.

        Returns:
            The prime limit of the lattice

        Examples:
            >>> JustLattice(60).prime_limit
            7
        """
        if not is_prime(value):
            msg = "Prime limit must be a prime number. "
            msg += "Got '{}'".format(value)
        self._prime_limit = value

    @property
    def fundamental(self) -> float:
        """Fundamental (1/1) pitch in Hertz.

        Returns:
            The fundamental's frequency in Hertz

        Examples:
            >>> JustLattice(60.0).fundamental
            60.0
        """
        return self._fundamental

    @fundamental.setter
    def fundamental(self, value: float):
        """Set the fundamental (1/1) pitch in Hertz."""
        try:
            self._fundamental = float(value)
            self._pitch = self._fundamental * self._tone
        except ValueError:
            msg = "Fundamental must be numeric. Got '{}'.".format(type(value))
            raise ValueError(msg)

    @property
    def hertz(self) -> float:
        """Current node's pitch in Hertz.

        Returns:
            The current node's pitch in Hertz

        Examples:
            >>> lattice = JustLattice(60)
            >>> lattice.traverse([1, 0, 0]).hertz
            90.0
        """
        return self._fundamental * self._tone

    @property
    def cents(self) -> float:
        """Current node's interval in Cents.

        Returns:
            The current node's interval in Cents

        Examples:
            >>> lattice = JustLattice(60)
            >>> round(lattice.traverse([1, 0, 0]).cents, 3)
            701.955
        """
        return self._tone.cents

    @property
    def tone(self) -> JustInterval:
        """Current node's tone.

        Returns:
            The current node's tone as a JustInterval

        Examples:
            >>> lattice = JustLattice(60)
            >>> lattice.traverse([1, 0, 0]).tone
            JustInterval(3, 2)
        """
        return self._tone

    @property
    def node(self) -> List[int]:
        """Current node as a vector with length equivalent to number of axes.

        Returns:
            The current node as a vector with length equivalent to number of axes

        Examples:
            >>> lattice = JustLattice(60)
            >>> lattice.traverse([0, 2, 3]).node
            [0, 2, 3]
        """
        return self._node

    @property
    def path(self) -> List[List[int]]:
        """Current traversal history.

        Returns:
            The traversal history across the lattice

        Examples:
            >>> lattice = JustLattice(60)
            >>> lattice.traverse([0, 2, 3]).path
            [[0, 0, 0], [0, 2, 3]]
        """
        return self._path

    def __repr__(self):
        """repr(self)"""
        return "{}({} Hz, {}/{}, {} Hz)".format(
            self.__class__.__name__,
            self.fundamental,
            self.tone.numerator,
            self.tone.denominator,
            round(self.hertz, 4),
        )
