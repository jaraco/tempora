v5.6.0
======

Features
--------

- Removed dependency on pytz. (#29)
- In utc.now(), bind late to allow for monkeypatching. (#31)


v5.5.1
======

Bugfixes
--------

- Remove test dependency on backports.unittest_mock. (#26)


v5.5.0
======

Features
--------

- Stopwatch now uses ``time.monotonic``.


v5.4.0
======

Features
--------

- Require Python 3.8 or later.


v5.3.0
======

#24: Removed use of ``datetime.utc**`` functions
deprecated in Python 3.12.

v5.2.2
======

#22: Fixed bug in tests that would fail when a leap year
was about a year away.

v5.2.1
======

#21: Restored dependency on ``jaraco.functools``, still
used in timing module.

v5.2.0
======

Remove dependency on jaraco.functools.

v5.1.1
======

Packaging refresh.

v5.1.0
======

Introduced ``infer_datetime`` and added some type hints.

v5.0.2
======

- Refreshed project.
- Enrolled with Tidelift.

v5.0.1
======

- Refreshed project.

v5.0.0
======

- Removed deprecated ``divide_*`` functions and ``Parser``
  class.
- Require Python 3.7 or later.
- #19: Fixed error reporting in parse_timedelta.

v4.1.2
======

- #18: Docs now build without warnings.

v4.1.1
======

- Fixed issue where digits were picked up in the unit when
  adjacent to the last unit.

v4.1.0
======

- Added support for more formats in ``parse_timedelta``.
- #17: ``parse_timedelta`` now supports formats emitted by
  ``timeit``, including honoring nanoseconds at the
  microsecond resolution.

v4.0.2
======

- Refreshed package metadata.

v4.0.1
======

- Refreshed package metadata.

v4.0.0
======

- Removed ``strptime`` function in favor of
  `datetime.datetime.strptime <https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime>`_. If passing
  a ``tzinfo`` parameter, instead invoke `.replace(tzinfo=...)`
  on the result.
- Deprecated ``divide_timedelta`` and ``divide_timedelta_float``
  now that Python supports this functionality natively.
- Deprecated ``Parser`` class. The
  `dateutil.parser <https://dateutil.readthedocs.io/en/stable/parser.html>`_
  provides more sophistication.

v3.0.0
======

- #10: ``strftime`` now reverts to the stdlib behavior for
  ``%u``. Use tempora 2.1 or later and the ``%µ`` for
  microseconds.

v2.1.1
======

- #8: Fixed error in ``PeriodicCommandFixedDelay.daily_at``
  when timezone is more than 12 hours from UTC.

v2.1.0
======

- #9: Fixed error when date object is passed to ``strftime``.
- #11: ``strftime`` now honors upstream expectation of
  rendering date values on time objects and vice versa.
- #10: ``strftime`` now honors ``%µ`` for rendering just
  the "microseconds" as ``%u`` supported previously.
  In a future, backward-incompatible release, the
  ``%u`` behavior will revert to the behavior as found
  in stdlib.

v2.0.0
======

* Require Python 3.6 or later.
* Removed DatetimeConstructor.

1.14.1
======

#7: Fix failing doctest in ``parse_timedelta``.

1.14
====

Package refresh, including use of declarative config in
the package metadata.

1.13
====

Enhancements to BackoffDelay:

 - Added ``.reset`` method.
 - Made iterable to retrieve delay values.

1.12
====

Added UTC module (Python 3 only), inspired by the
`utc project <https://pypi.org/project/utc>`_.

1.11
====

#5: Scheduler now honors daylight savings times in the
    PeriodicCommands.

1.10
====

Added ``timing.BackoffDelay``, suitable for implementing
exponential backoff delays, such as those between retries.

1.9
===

Added support for months, years to ``parse_timedelta``.

1.8
===

Introducing ``timing.Timer``, featuring a ``expired``
method for detecting when a certain duration has been
exceeded.

1.7.1
=====

#3: Stopwatch now behaves reliably during timezone
    changes and (presumably) daylight savings time
    changes.

1.7
===

Update project skeleton.

1.6
===

Adopt ``irc.schedule`` as ``tempora.schedule``.

1.5
===

Adopt ``jaraco.timing`` as ``tempora.timing``.

Automatic deployment with Travis-CI.

1.4
===

Moved to Github.

Improved test support on Python 2.

1.3
===

Added divide_timedelta from ``svg.charts``.
Added date_range from ``svg.charts``.
