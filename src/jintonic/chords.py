"""Implements just intonation chords."""
from __future__ import annotations

from copy import deepcopy
from typing import List

from .harmonics import harmonic_segment_to_identities, tones_to_harmonic_segment
from .intervals import JustInterval
from .lattice import JustLattice
from .primes import generate_primes


class JustLatticeChord:
    """This class implements chords based on lattice coordinates."""

    def __init__(
        self,
        fundamental: float,
        root: List[int],
        nodes: List[List[int]],
    ):
        """Initializes a JustLatticeChord.

        Parameters:
            fundamental: Fundamental pitch in Hertz.
            root: Root lattice node (the chord's root tone)
            nodes: Lattice nodes of each constituent chord tone.

        Examples:
            >>> nodes = [[-1, 0, 1], [1, 0, 0], [0, 0, 1]]
            >>> JustLatticeChord(fundamental=100.0, root=[1, 0, 0], nodes=nodes)
            JustLatticeChord(100.0 Hz, [3/2, 7/4, 9/8, 21/16], [3-7-9-21])
        """
        self._fundamental: float = float(fundamental)
        self._nodes = nodes
        self._root = root
        self.lattice = JustLattice(fundamental=self._fundamental)

    @classmethod
    def from_name(
        cls,
        fundamental: float,
        root: List[int],
        name: str,
    ) -> JustLatticeChord:
        """Initializes a JustLatticeChord from a conventional chord name.

        Parameters:
            fundamental: The fundamental frequency in Hertz
            root: The root node lattice coordinates
            name: The chord name

        Returns:
            A JustLatticeChord

        The list of valid names is:
            - "sub-minor triad"
            - "minor triad"
            - "diminished triad"
            - "major triad"
            - "sub-minor seventh"
            - "minor seventh"
            - "half-diminished seventh"
            - "major seventh"
            - "super-major seventh"
            - "dominant seventh"
            - "added second"
            - "minor ninth"
            - "major ninth"
            - "dominant ninth"
            - "4-6-7"
            - "5-7-9"

        Examples:

            >>> JustLatticeChord.from_name(60, [0, 0, 0], 'minor triad')
            JustLatticeChord(60.0 Hz, [1/1, 6/5, 3/2], [5-3-15])

            >>> JustLatticeChord.from_name(60, [-1, 0, 0], 'major triad')
            JustLatticeChord(60.0 Hz, [4/3, 5/3, 1/1], [1-5-3])
        """
        nodes = {
            "sub-minor triad": [[1, 0, 0], [-1, 0, 1]],
            "minor triad": [[1, -1, 0], [1, 0, 0]],
            "diminished triad": [[1, -1, 0], [0, -1, 1]],
            "major triad": [[0, 1, 0], [1, 0, 0]],
            "sub-minor seventh": [[-1, 0, 1], [1, 0, 0], [0, 0, 1]],
            "minor seventh": [[1, -1, 0], [1, 0, 0], [2, -1, 0]],
            "half-diminished seventh": [[1, -1, 0], [0, -1, 1], [2, -1, 0]],
            "major seventh": [[0, 1, 0], [1, 0, 0], [1, 1, 0]],
            "super-major seventh": [[2, 0, -1], [1, 0, 0], [3, 0, -1]],
            "dominant seventh": [[0, 1, 0], [1, 0, 0], [1, 1, 0], [0, 0, 1]],
            "added second": [[0, 1, 0], [1, 0, 0], [2, -1, 0]],
            "minor ninth": [[1, -1, 0], [1, 0, 0], [2, -1, 0], [2, 0, 0]],
            "major ninth": [[0, 1, 0], [1, 0, 0], [1, 1, 0], [2, 0, 0]],
            "dominant ninth": [[0, 1, 0], [1, 0, 0], [0, 0, 1], [2, 0, 0]],
            "4-6-7": [[1, 0, 0], [0, 0, 1]],
            "5-7-9": [[0, -1, 1], [2, -1, 0]],
        }
        try:
            return cls(fundamental, root, nodes[name.lower()])
        except KeyError:
            return NotImplemented

    def transpose(self, node: List[int]) -> JustLatticeChord:
        """JustLatticeChord transposition.

        Parameters:
            node: The target root node of the transposed chord.

        Returns:
            A transposed JustLatticeChord

        Note:
            Returns a copy

        Examples:
            >>> chord = JustLatticeChord.from_name(60, [0, 0, 0], 'minor triad')
            >>> node = [1, 0, 0]
            >>> chord.transpose(node)
            JustLatticeChord(60.0 Hz, [3/2, 9/5, 9/8], [5-3-15])
        """
        chord = deepcopy(self)
        chord.root = node
        chord.lattice.to_node((node))

        return chord

    def pivot(self, axis: int = 3) -> JustLatticeChord:
        """Pivots the JustLatticeChord along the given axis.

        Parameters:
            axis: Prime limit axis (a prime number)

        Returns:
            A pivoted JustLatticeChord

        Note:
            Returns a copy

        Examples:
            >>> chord = JustLatticeChord.from_name(60, [0, 0, 0], 'major triad')
            >>> chord.pivot(3)
            JustLatticeChord(60.0 Hz, [1/1, 5/4, 4/3], [3-15-1])
        """
        if axis > self.prime_limit:
            raise ValueError(
                "Cannot pivot on an axis greater than the chord's prime limit."
            )
        chord = deepcopy(self)
        axis_ix = generate_primes(chord.prime_limit)[1:].index(axis)
        base = min(node[axis_ix] for node in chord._nodes)
        base = 0
        for i, node in enumerate(chord._nodes):
            node[axis_ix] = base - node[axis_ix]
            chord._nodes[i] = node
        return chord

    @property
    def fundamental(self):
        return self._fundamental

    @property
    def nodes(self):
        """JustLatticeChord nodes."""
        return self._nodes

    @nodes.setter
    def nodes(self, values: List[List[int]]):
        """JustLatticeChord nodes.

        Parameters:
            values: Constituent lattice nodes.
        """
        """Sets (and expands) JustLatticeChord nodes."""
        max_len = max((len(node) for node in values))
        self._nodes = []
        for node in values:
            self._nodes.append(node + (max_len - len(node)) * [0])

    @property
    def root(self):
        """JustLatticeChord root node."""
        return self._root

    @root.setter
    def root(self, value: List[int]):
        """Sets (and expands) JustLatticeChord root node.

        Parameters:
            value: Root lattice node
        """
        max_len = max((len(node) for node in self._nodes))
        self._root = value + (max_len - len(value)) * [0]

    @property
    def tones(self) -> List[JustInterval]:
        """JustLatticeChord constituent intervals from root (tones).

        Returns:
            The tones of the chord as JustIntervals from the fundamental.

        Examples:
            >>> chord = JustLatticeChord.from_name(60, [0, 0, 0], 'major triad')
            >>> chord.tones
            [JustInterval(1, 1), JustInterval(5, 4), JustInterval(3, 2)]
        """
        tones = []
        self.lattice.to_node(self._root)
        root_tone = self.lattice.tone
        tones.append(root_tone)
        for node in self._nodes:
            self.lattice.to_node(self._root)
            constituent = self.lattice.traverse(node)
            constituent_tone = constituent.tone
            tones.append(constituent_tone)
        self.lattice.to_node(self._root)

        return tones

    @property
    def prime_limit(self) -> int:
        """JustLatticeChord prime limit."""
        return max([tone.prime_limit for tone in self.tones])

    @property
    def harmonics(self) -> List[int]:
        """JustLatticeChord harmonics (relative frequencies).

        Returns:
            The lattice's prime limit

        Examples:
            >>> chord = JustLatticeChord.from_name(60, [0, 0, 0], 'minor triad')
            >>> chord.harmonics
            [10, 12, 15]
        """
        return tones_to_harmonic_segment(self.tones)

    @property
    def identities(self) -> List[int]:
        """JustLatticeChord constituent identities.

        Returns:
            The constituent identities

        Examples:
            >>> chord = JustLatticeChord.from_name(60, [0, 0, 0], 'minor triad')
            >>> chord.identities
            [5, 3, 15]
        """
        return harmonic_segment_to_identities(self.harmonics)

    @property
    def hertz(self) -> List[float]:
        """JustLatticeChord constituent Hertz values.

        Returns:
            The frequencies in Hertz of the constituent pitches

        Examples:
            >>> chord = JustLatticeChord.from_name(60, [0, 0, 0], 'minor triad')
            >>> chord.hertz
            [60.0, 72.0, 90.0]
        """
        tones = [self.tones[0]]
        for tone in self.tones[1:]:
            while tone < tones[-1]:
                tone += JustInterval(2, 1)
            tones.append(tone)
        return [self._fundamental * tone for tone in tones]

    @property
    def complement(self) -> JustLatticeChord:
        """JustLatticeChord complement.

        Every node's relationship to the root node is inverted.

        Returns:
            A JustLatticeChord that is the complement of this one

        Note:
            Returns a copy.

        Examples:
            >>> nodes = [[2, 0], [0, 1], [-1, 0], [1, 0]]
            >>> chord = JustLatticeChord(60, [0, 0, 0], nodes)
            >>> chord.complement
            JustLatticeChord(60.0 Hz, [1/1, 16/9, 8/5, 3/2, 4/3], [45-5-9-135-15])
        """
        nodes = []
        for node in self._nodes:
            nodes.append(list(map(lambda x, y: y - x, node, self._root)))
        return JustLatticeChord(self._fundamental, self._root, nodes)

    def __repr__(self):
        """repr(self)"""
        tones = ", ".join(
            [
                "/".join([str(tone.numerator), str(tone.denominator)])
                for tone in self.tones
            ]
        )
        identities = ", ".join(
            ["-".join([str(identity) for identity in self.identities])]
        )
        return "{}({} Hz, [{}], [{}])".format(
            self.__class__.__name__, self._fundamental, tones, identities
        )
