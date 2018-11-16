scales
------

Implements just intonation scales, and scale components.

JustScale
================

.. autoclass:: jintonic.scales.JustScale

  .. automethod:: jintonic.scales.JustScale.__init__
  .. automethod:: jintonic.scales.JustScale.append
  .. automethod:: jintonic.scales.JustScale.hertz
  .. autoattribute:: jintonic.scales.JustScale.tones
  .. autoattribute:: jintonic.scales.JustScale.intervals
  .. autoattribute:: jintonic.scales.JustScale.complement
  .. autoattribute:: jintonic.scales.JustScale.prime_limit
  .. autoattribute:: jintonic.scales.JustScale.pitch_mapping

----

JustTetrachord
==============

.. autoclass:: jintonic.scales.JustTetrachord

  .. automethod:: jintonic.scales.JustTetrachord.__init__
  .. automethod:: jintonic.scales.JustTetrachord.validate_tetrachord
  .. autoattribute:: jintonic.scales.JustTetrachord.genus
  .. autoattribute:: jintonic.scales.JustTetrachord.prime_limit
  .. autoattribute:: jintonic.scales.JustTetrachord.permutations
  .. autoattribute:: jintonic.scales.JustTetrachord.intervals

----

JustTetrachordalScale
=====================

.. autoclass:: jintonic.scales.JustTetrachordalScale

  .. automethod:: jintonic.scales.JustTetrachordalScale.__init__
  .. automethod:: jintonic.scales.JustTetrachordalScale.hertz
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.lower
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.upper
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.genera
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.tones
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.intervals
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.complement
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.prime_limit
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.permutations
  .. autoattribute:: jintonic.scales.JustTetrachordalScale.pitch_mapping
