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
