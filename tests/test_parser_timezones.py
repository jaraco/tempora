import datetime

import pytest
import tempora


@pytest.mark.parametrize(
    'tzinfos',
    [
        {'XST': 3600},
        lambda name, offset: datetime.timezone(datetime.timedelta(hours=1)),
    ],
)
def test_parse_custom_timezone(tzinfos) -> None:
    parsed = tempora.parse('2024-01-01 12:00 XST', tzinfos=tzinfos)
    assert parsed.utcoffset() == datetime.timedelta(hours=1)


def test_parse_timezone_override() -> None:
    parsed = tempora.parse('2024-01-01 12:00 EST', tzinfos={'EST': 3600})
    assert parsed.utcoffset() == datetime.timedelta(hours=1)


def test_parse_explicit_none_timezone_mapping() -> None:
    parsed = tempora.parse('2024-01-01T12:00:00+01:00', tzinfos=None)
    assert parsed.utcoffset() == datetime.timedelta(hours=1)


def test_parse_default_timezone_mapping() -> None:
    parsed = tempora.parse('2024-01-01 12:00 EST')
    assert parsed.utcoffset() == datetime.timedelta(hours=-5)
