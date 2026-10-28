import datetime
import decimal

import pytest
import tempora


@pytest.mark.parametrize(
    'spec,nanoseconds',
    [
        ('-1 second', '-1000000000'),
        ('-1 ms', '-1000000'),
        ('-.5 us', '-500'),
        ('-600 ns', '-600'),
        ('1 second, -2 milliseconds', '998000000'),
        ('-1:30:00', '-5400000000000'),
        ('+1:30:00', '5400000000000'),
        ('1 second', '1000000000'),
    ],
)
def test_signed_duration_parsing(spec: str, nanoseconds: str) -> None:
    expected = decimal.Decimal(nanoseconds)
    assert tempora.parse_nanoseconds(spec) == expected
    assert tempora.Duration.parse(spec).nanoseconds == expected
    assert tempora.parse_timedelta(spec) == datetime.timedelta(
        microseconds=round(expected / 1000)
    )
