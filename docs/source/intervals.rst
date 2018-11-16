intervals
---------

Implements just intonation intervals (ratios).

JustInterval
============

.. autoclass:: jintonic.intervals.JustInterval

  .. automethod:: jintonic.intervals.JustInterval.__init__
  .. automethod:: jintonic.intervals.JustInterval.from_two_hertz
  .. automethod:: jintonic.intervals.JustInterval.divisions
  .. autoattribute:: jintonic.intervals.JustInterval.numerator
  .. autoattribute:: jintonic.intervals.JustInterval.denominator
  .. autoattribute:: jintonic.intervals.JustInterval.prime_limit
  .. autoattribute:: jintonic.intervals.JustInterval.is_superparticular
  .. autoattribute:: jintonic.intervals.JustInterval.base_octave
  .. autoattribute:: jintonic.intervals.JustInterval.complement
  .. autoattribute:: jintonic.intervals.JustInterval.cents
  .. automethod:: jintonic.intervals.JustInterval.__add__
  .. automethod:: jintonic.intervals.JustInterval.__radd__
  .. automethod:: jintonic.intervals.JustInterval.__sub__
  .. automethod:: jintonic.intervals.JustInterval.__rmul__
  .. automethod:: jintonic.intervals.JustInterval.__pow__
  .. automethod:: jintonic.intervals.JustInterval.__truediv__
  .. automethod:: jintonic.intervals.JustInterval.__eq__
  .. automethod:: jintonic.intervals.JustInterval.__lt__
  .. automethod:: jintonic.intervals.JustInterval.__gt__
  .. automethod:: jintonic.intervals.JustInterval.__le__
  .. automethod:: jintonic.intervals.JustInterval.__ge__
  .. automethod:: jintonic.intervals.JustInterval.__bool__

----

Functions
=========

.. autofunction:: jintonic.intervals.primary_interval
