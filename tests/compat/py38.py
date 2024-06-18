import sys


if sys.version_info >= (3, 9):
    import zoneinfo
else:  # pragma: no cover
    from backports import zoneinfo  # noqa: F401
