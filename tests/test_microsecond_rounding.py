import datetime

import pytest
import tempora


@pytest.mark.parametrize(
    ("period_us", "offset_us", "expected_us"),
    [(1, 0, 0), (1, 7, 7), (3, 1, 0), (3, 2, 3), (4, 2, 4), (5, 2, 0)],
)
def test_microsecond_rounding(period_us: int, offset_us: int, expected_us: int) -> None:
    start = datetime.datetime(2024, 1, 1)  # noqa: DTZ001
    result = tempora.datetime_round(
        start + datetime.timedelta(microseconds=offset_us),
        datetime.timedelta(microseconds=period_us),
        start,
    )
    assert result == start + datetime.timedelta(microseconds=expected_us)
