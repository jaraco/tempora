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
