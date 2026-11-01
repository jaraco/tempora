import datetime
import random
import time
import zoneinfo
from collections.abc import Callable
from unittest import mock

import freezegun
import pytest
from tempora import schedule

do_nothing = type(None)


def test_delayed_command_order() -> None:
    """
    delayed commands should be sorted by delay time
    """
    delays = [random.randint(0, 99) for x in range(5)]
    cmds = sorted(schedule.DelayedCommand.after(delay, do_nothing) for delay in delays)
    assert [c.delay.seconds for c in cmds] == sorted(delays)


def test_periodic_command_delay() -> None:
    "A PeriodicCommand must have a positive, non-zero delay."
    with pytest.raises(ValueError) as exc_info:
        schedule.PeriodicCommand.after(0, None)
    assert str(exc_info.value) == test_periodic_command_delay.__doc__


def test_periodic_command_fixed_delay() -> None:
    """
    Test that we can construct a periodic command with a fixed initial
    delay.
    """
    fd = schedule.PeriodicCommandFixedDelay.at_time(
        at=schedule.now(), delay=datetime.timedelta(seconds=2), target=lambda: None
    )
    assert fd.due() is True
    assert fd.next().due() is False


class TestCommands:
    def test_delayed_command_from_timestamp(self) -> None:
        """
        Ensure a delayed command can be constructed from a timestamp.
        """
        t = time.time()
        schedule.DelayedCommand.at_time(t, do_nothing)

    def test_command_at_noon(self) -> None:
        """
        Create a periodic command that's run at noon every day.
        """
        when = datetime.time(12, 0, tzinfo=zoneinfo.ZoneInfo('UTC'))
        cmd = schedule.PeriodicCommandFixedDelay.daily_at(when, target=None)
        assert cmd.due() is False
        next_cmd = cmd.next()
        daily = datetime.timedelta(days=1)
        day_from_now = schedule.now() + daily
        two_days_from_now = day_from_now + daily
        assert day_from_now < next_cmd < two_days_from_now

    @pytest.mark.parametrize("hour", range(10, 14))
    @pytest.mark.parametrize("tz_offset", (14, -14))
    def test_command_at_noon_distant_local(self, hour: int, tz_offset: int) -> None:
        """
        Run test_command_at_noon, but with the local timezone
        more than 12 hours away from UTC.
        """
        with freezegun.freeze_time(f"2020-01-10 {hour:02}:01", tz_offset=tz_offset):
            self.test_command_at_noon()


class TestTimezones:
    def test_alternate_timezone_west(self) -> None:
        target_tz = zoneinfo.ZoneInfo('US/Pacific')
        target = schedule.now().astimezone(target_tz)
        cmd = schedule.DelayedCommand.at_time(target, target=None)
        assert cmd.due()

    def test_alternate_timezone_east(self) -> None:
        target_tz = zoneinfo.ZoneInfo('Europe/Amsterdam')
        target = schedule.now().astimezone(target_tz)
        cmd = schedule.DelayedCommand.at_time(target, target=None)
        assert cmd.due()

    def test_daylight_savings(self) -> None:
        """
        A command at 9am should always be 9am regardless of
        a DST boundary.
        """
        with freezegun.freeze_time('2018-03-10'):
            target_tz = zoneinfo.ZoneInfo('US/Eastern')
            target_time = datetime.time(9, tzinfo=target_tz)
            cmd = schedule.PeriodicCommandFixedDelay.daily_at(
                target_time, target=lambda: None
            )
            assert not cmd.due()

        def naive(dt: datetime.datetime) -> datetime.datetime:
            return dt.replace(tzinfo=None)

        assert naive(cmd) == datetime.datetime(2018, 3, 10, 9, 0, 0)  # noqa: DTZ001

        with freezegun.freeze_time('2018-03-10 8:59:59 -0500'):
            assert not cmd.due()

        with freezegun.freeze_time('2018-03-10 9:00:00 -0500'):
            assert cmd.due()

        next_ = cmd.next()

        assert naive(next_) == datetime.datetime(2018, 3, 11, 9, 0, 0)  # noqa: DTZ001

        with freezegun.freeze_time('2018-03-11 8:59:59 -0400'):
            assert not next_.due()

        with freezegun.freeze_time('2018-03-11 9:00:00 -0400'):
            assert next_.due()


class TestScheduler:
    def test_invoke_scheduler(self) -> None:
        sched = schedule.InvokeScheduler()
        target = mock.MagicMock()
        cmd = schedule.DelayedCommand.after(0, target)
        sched.add(cmd)
        sched.run_pending()
        target.assert_called_once()
        assert not sched.queue

    def test_callback_scheduler(self) -> None:
        callback = mock.MagicMock()
        sched = schedule.CallbackScheduler(callback)
        target = mock.MagicMock()
        cmd = schedule.DelayedCommand.after(0, target)
        sched.add(cmd)
        sched.run_pending()
        callback.assert_called_once_with(target)

    def test_periodic_command(self) -> None:
        sched = schedule.InvokeScheduler()
        target = mock.MagicMock()

        before = datetime.datetime.now(tz=datetime.timezone.utc)

        cmd = schedule.PeriodicCommand.after(10, target)
        sched.add(cmd)
        sched.run_pending()
        target.assert_not_called()

        with freezegun.freeze_time(before + datetime.timedelta(seconds=15)):
            sched.run_pending()
        assert sched.queue
        target.assert_called_once()

        with freezegun.freeze_time(before + datetime.timedelta(seconds=25)):
            sched.run_pending()
        assert target.call_count == 2


@pytest.fixture(params=['from_datetime', 'at_time', 'fixed_delay_at_time'])
def command_constructor(
    request: pytest.FixtureRequest,
) -> tuple[
    Callable[[datetime.datetime], schedule.DelayedCommand],
    type[schedule.DelayedCommand],
]:
    if request.param == 'from_datetime':
        return schedule.DelayedCommand.from_datetime, schedule.DelayedCommand
    if request.param == 'at_time':
        return (
            lambda value: schedule.DelayedCommand.at_time(value, None),
            schedule.DelayedCommand,
        )
    return (
        lambda value: schedule.PeriodicCommandFixedDelay.at_time(
            value, datetime.timedelta(hours=1), None
        ),
        schedule.PeriodicCommandFixedDelay,
    )


@pytest.mark.parametrize('fold', [0, 1, None], ids=['first', 'second', 'utc'])
def test_command_preserves_datetime(
    command_constructor: tuple[
        Callable[[datetime.datetime], schedule.DelayedCommand],
        type[schedule.DelayedCommand],
    ],
    fold: int | None,
) -> None:
    constructor, command_type = command_constructor
    zone = zoneinfo.ZoneInfo('America/New_York') if fold is not None else datetime.UTC
    value = datetime.datetime(
        2024, 11, 3, 1, 30, 15, 123456, tzinfo=zone, fold=fold or 0
    )

    command = constructor(value)

    assert type(command) is command_type
    assert command.fold == value.fold
    assert command.tzinfo is zone
    assert command.microsecond == value.microsecond
    assert command.utcoffset() == value.utcoffset()
    assert command.timestamp() == value.timestamp()
    assert (
        command.astimezone(datetime.UTC).isoformat()
        == value.astimezone(datetime.UTC).isoformat()
    )


def test_command_from_numeric_timestamp() -> None:
    value = datetime.datetime(
        2024,
        11,
        3,
        1,
        30,
        15,
        123456,
        tzinfo=zoneinfo.ZoneInfo('America/New_York'),
        fold=1,
    )

    command = schedule.DelayedCommand.at_time(value.timestamp(), None)

    assert command.timestamp() == value.timestamp()
    assert command.tzinfo is datetime.UTC
    assert command.microsecond == value.microsecond


@pytest.mark.parametrize('fold,expected_due', [(0, True), (1, False)])
def test_command_due_in_ambiguous_hour(
    command_constructor: tuple[
        Callable[[datetime.datetime], schedule.DelayedCommand],
        type[schedule.DelayedCommand],
    ],
    fold: int,
    expected_due: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = datetime.datetime(2024, 11, 3, 5, 45, tzinfo=datetime.UTC)
    monkeypatch.setattr(schedule, 'now', lambda: now)
    value = datetime.datetime(
        2024,
        11,
        3,
        1,
        30,
        tzinfo=zoneinfo.ZoneInfo('America/New_York'),
        fold=fold,
    )
    constructor, _ = command_constructor

    command = constructor(value)

    assert command.due() is expected_due
