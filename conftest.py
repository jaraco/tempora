import sys
import operator


def pytest_collection_modifyitems(session, config, items):
    remove_parse_timedelta(items)


def remove_parse_timedelta(items):  # pragma: nocover
    """
    Repr on older Pythons is different, so remove the offending
    test.
    """
    if sys.version_info > (3, 7):
        return
    names = list(map(operator.attrgetter('name'), items))
    del items[names.index('tempora.parse_timedelta')]
