"""
Facilities for common time operations in UTC.

Inspired by the `utc project <https://pypi.org/project/utc>`_.

>>> dt = now()
>>> dt == fromtimestamp(dt.timestamp())
True
>>> dt.tzinfo
datetime.timezone.utc

>>> from time import time as timestamp
>>> now().timestamp() - timestamp() < 0.1
True

>>> (now() - fromtimestamp(timestamp())).total_seconds() < 0.1
True

>>> datetime(2018, 6, 26, 0).tzinfo
datetime.timezone.utc

>>> time(0, 0).tzinfo
datetime.timezone.utc

These operations should be affected by freezegun.

>>> freezer = getfixture('freezer')
>>> freezer.move_to('2000-01-01 00:00:00 -0700')
>>> now()
datetime.datetime(2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
"""

import datetime as std
import functools


__all__ = ['now', 'fromtimestamp', 'datetime', 'time']


now = functools.partial(std.datetime.now, std.timezone.utc)
fromtimestamp = functools.partial(std.datetime.fromtimestamp, tz=std.timezone.utc)
datetime = functools.partial(std.datetime, tzinfo=std.timezone.utc)
time = functools.partial(std.time, tzinfo=std.timezone.utc)
