import datetime
import zoneinfo

import pytest
import tempora


@pytest.mark.parametrize(
    "zone",
    [
        datetime.timezone.utc,
        datetime.timezone(datetime.timedelta(hours=5, minutes=30)),
        zoneinfo.ZoneInfo("America/New_York"),
    ],
)
def test_default_midnight_preserves_timezone(zone: datetime.tzinfo) -> None:
    value = datetime.datetime(2024, 3, 10, 13, 40, tzinfo=zone)
    period = datetime.timedelta(hours=1)
    assert tempora.datetime_mod(value, period) == value.replace(minute=0)
    assert tempora.datetime_round(value, period) == value.replace(hour=14, minute=0)
    assert tempora.datetime_mod(value, period).tzinfo is zone


def test_naive_default_midnight() -> None:
    value = datetime.datetime(2024, 3, 10, 13, 40)  # noqa: DTZ001
    assert tempora.datetime_mod(value, datetime.timedelta(hours=1)) == value.replace(
        minute=0
    )
