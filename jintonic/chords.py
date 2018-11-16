"""Implements just intonation chords."""

from copy import deepcopy

from .intervals import JustInterval
from .primes import generate_primes
from .lattice import JustLattice
from .harmonics import tones_to_harmonic_segment
from .harmonics import harmonic_segment_to_identities


__version__ = '0.0.1'


class JustLatticeChord():
    """This class implements chords based on lattice coordinates."""

    def __init__(self, nodes, fundamental=60, root=(0, )):
        """Initializes a JustLatticeChord.

        :param nodes: Lattice nodes of each constituent chord tone.
        :type nodes: list of tuple
        :param fundamental: Fundamental pitch in Hertz.
        :type fundamental: float
        :param root: Root lattice node (the chord's root tone)
        :type root: tuple

        **Examples**

        >>> nodes = [(-1, 0, 1), (1, ), (0, 0, 1)]
        >>> JustLatticeChord(nodes, fundamental=100, root=(1, ))
        JustLatticeChord(100 - [3/2, 7/4, 9/8, 21/16], [3-7-9-21])
        """
        self._fundamental = None
        self._root = None
        self._nodes = None

        self.fundamental = fundamental
        self.nodes = nodes
        self.root = root
        self.lattice = JustLattice(fundamental=self.fundamental)

    @classmethod
    def from_name(cls, name, fundamental=60, root=(0, )):
        """Initializes a JustLatticeChord from a conventional chord name.

        **Examples**

        >>> JustLatticeChord.from_name('minor triad')
        JustLatticeChord(60 - [1/1, 6/5, 3/2], [5-3-15])

        >>> JustLatticeChord.from_name('major triad', root=(-1, ))
        JustLatticeChord(60 - [4/3, 5/3, 1/1], [1-5-3])
        """
        names = {
            'sub-minor triad': cls(
                [(1, ), (-1, 0, 1)],
                fundamental, root),
            'minor triad': cls(
                [(1, -1), (1, )],
                fundamental, root),
            'diminished triad': cls(
                [(1, -1), (0, -1, 1)],
                fundamental, root),
            'major triad': cls(
                [(0, 1), (1, )],
                fundamental, root),
            'sub-minor seventh': cls(
                [(-1, 0, 1), (1, ), (0, 0, 1)],
                fundamental, root),
            'minor seventh': cls(
                [(1, -1), (1, ), (2, -1)],
                fundamental, root),
            'half-diminished seventh': cls(
                [(1, -1), (0, -1, 1), (2, -1)],
                fundamental, root),
            'major seventh': cls(
                [(0, 1), (1, ), (1, 1)],
                fundamental, root),
            'super-major seventh': cls(
                [(2, 0, -1), (1, ), (3, 0, -1)],
                fundamental, root),
            'dominant seventh': cls(
                [(0, 1), (1, ), (1, 1), (0, 0, 1)],
                fundamental, root),
            'added second': cls(
                [(0, 1), (1, ), (2, -1)],
                fundamental, root),
            'minor ninth': cls(
                [(1, -1), (1, ), (2, -1), (2, )],
                fundamental, root),
            'major ninth': cls(
                [(0, 1), (1, ), (1, 1), (2, )],
                fundamental, root),
            'dominant ninth': cls(
                [(0, 1), (1, ), (0, 0, 1), (2, )],
                fundamental, root),
            '4-6-7': cls(
                [(1, ), (0, 0, 1)],
                fundamental, root),
            '5-7-9': cls(
                [(0, -1, 1), (2, -1)],
                fundamental, root),
        }
        try:
            return names[name.lower()]
        except KeyError:
            return NotImplemented

    def transpose(self, node):
        """JustLatticeChord transposition.

        Returns a copy

        :param node: The target root node of the transposed chord.
        :type node: tuple

        :rtype: JustLatticeChord

        **Examples**

        >>> chord = JustLatticeChord.from_name('minor triad')
        >>> node = (1, )
        >>> chord.transpose(node)
        JustLatticeChord(60 - [3/2, 9/5, 9/8], [5-3-15])
        """
        chord = deepcopy(self)
        chord.root = node
        chord.lattice.to_node(*node)

        return chord

    def pivot(self, axis=3):
        """Pivots the JustLatticeChord wither vertically or horizontally.

        Returns a copy.

        :param axis: Prime limit axis (a prime number)
        :type axis: int

        :rtype: JustLatticeChord

        **Examples**

        >>> chord = JustLatticeChord.from_name('major triad')
        >>> chord.pivot(3)
        JustLatticeChord(60 - [1/1, 8/5, 3/2], [5-1-15])
        """
        chord = deepcopy(self)
        axis_ix = generate_primes(chord.prime_limit)[1:].index(axis) + 1
        base = min(node[axis_ix] for node in chord.nodes)
        for i, node in enumerate(chord.nodes):
            node = list(node)
            node[axis_ix] = base - node[axis_ix]
            chord.nodes[i] = tuple(node)
        return chord

    @property
    def nodes(self):
        """JustLatticeChord nodes.

        :param values: Constituent lattice nodes.
        :type values: list of tuple

        :rtype: list of tuple
        """
        return self._nodes

    @nodes.setter
    def nodes(self, values):
        """Sets (and expands) JustLatticeChord nodes."""
        max_len = max((len(node) for node in values))
        self._nodes = []
        for node in values:
            self._nodes.append(
                node + tuple((max_len - len(node)) * [0])
            )

    @property
    def root(self):
        """JustLatticeChord root node.

        :param value: Root lattice node
        :type value: tuple


        :rtype: tuple
        """
        return self._root

    @root.setter
    def root(self, value):
        """Sets (and expands) JustLatticeChord root node."""
        max_len = max((len(node) for node in self.nodes))
        self._root = value + tuple((max_len - len(value)) * [0])

    @property
    def tones(self):
        """JustLatticeChord constituent intervals from root (tones).

        :rtype: list of JustInterval

        **Examples**


        >>> chord = JustLatticeChord.from_name('major triad')
        >>> chord.tones
        [JustInterval(1, 1), JustInterval(5, 4), JustInterval(3, 2)]
        """
        tones = []
        self.lattice.to_node(*self.root)
        root_tone = self.lattice.tone
        tones.append(root_tone)
        for node in self.nodes:
            self.lattice.to_node(*self.root)
            constituent = self.lattice.traverse(*node)
            constituent_tone = constituent.tone
            tones.append(constituent_tone)
        self.lattice.to_node(*self.root)

        return tones

    @property
    def prime_limit(self):
        """JustLatticeChord prime limit.

        :rtype: int
        """
        return max([tone.prime_limit for tone in self.tones])

    @property
    def harmonics(self):
        """JustLatticeChord harmonics (relative frequencies).

        :rtype: list of int

        **Examples**


        >>> chord = JustLatticeChord.from_name('minor triad')
        >>> chord.harmonics
        [10, 12, 15]
        """
        return tones_to_harmonic_segment(self.tones)

    @property
    def identities(self):
        """JustLatticeChord constituent identities.

        :rtype: list of int

        **Examples**


        >>> chord = JustLatticeChord.from_name('minor triad')
        >>> chord.identities
        [5, 3, 15]
        """
        return harmonic_segment_to_identities(self.harmonics)

    @property
    def hertz(self):
        """JustLatticeChord constituent Hertz values.

        :rtype: list of float

        **Examples**


        >>> chord = JustLatticeChord.from_name('minor triad')
        >>> chord.hertz
        [60.0, 72.0, 90.0]
        """
        tones = [self.tones[0]]
        for tone in self.tones[1:]:
            while tone < tones[-1]:
                tone += JustInterval(2, 1)
            tones.append(tone)
        return [self.fundamental * tone for tone in tones]

    @property
    def complement(self):
        """JustLatticeChord complement.

        Every node's relationship to the root node is inverted.

        Returns a copy.

        :rtype: JustLatticeChord

        **Examples**

        >>> chord = JustLatticeChord([(2, ), (0, 1), (-1, ), (1, )])
        >>> chord.complement
        JustLatticeChord(60 - [1/1, 16/9, 8/5, 3/2, 4/3], [45-5-9-135-15])
        """
        nodes = []
        for node in self.nodes:
            nodes.append(
                tuple(map(lambda x, y: y - x, node, self.root))
            )
        return JustLatticeChord(nodes, self.fundamental, self.root)

    def __repr__(self):
        """repr(self)

        (<fundamental> - [<tones>], [<identities>])
        """
        tones = ', '.join([
            '/'.join([str(tone.numerator), str(tone.denominator)])
            for tone in self.tones
        ])
        identities = ', '.join([
            '-'.join([str(identity) for identity in self.identities])
        ])
        return "{}({} - [{}], [{}])".format(
            self.__class__.__name__,
            self.fundamental,
            tones,
            identities
        )
