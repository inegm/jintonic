if __name__ == "__main__":
    import doctest
    from jintonic import chords as jichords
    from jintonic import harmonics as jiharmonics
    from jintonic import intervals as jiintervals
    from jintonic import lattice as jilattice
    from jintonic import primes as jiprimes
    from jintonic import scales as jiscales

    doctest.testmod(
        jichords,
        optionflags=doctest.NORMALIZE_WHITESPACE
    )
    doctest.testmod(
        jiharmonics,
        optionflags=doctest.NORMALIZE_WHITESPACE
    )
    doctest.testmod(
        jiintervals,
        optionflags=doctest.NORMALIZE_WHITESPACE
    )
    doctest.testmod(
        jilattice,
        optionflags=doctest.NORMALIZE_WHITESPACE
    )
    doctest.testmod(
        jiprimes,
        optionflags=doctest.NORMALIZE_WHITESPACE
    )
    doctest.testmod(
        jiscales,
        optionflags=doctest.NORMALIZE_WHITESPACE
    )
