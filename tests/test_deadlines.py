"""Tests for deadline classification boundaries in user story 2."""

from datetime import UTC, datetime, timedelta

import pytest

from app.deadlines import deadline_status


@pytest.fixture
def fixed_now():
    """Use a fixed aware instant so boundary checks do not depend on wall time."""
    return datetime(2026, 10, 26, 12, 0, 0, tzinfo=UTC)


def test_deadline_equal_to_now_is_overdue_not_urgent(fixed_now):
    assert deadline_status(fixed_now, fixed_now) == (True, False)


def test_deadline_one_microsecond_after_now_is_urgent(fixed_now):
    deadline = fixed_now + timedelta(microseconds=1)

    assert deadline_status(deadline, fixed_now) == (False, True)


def test_deadline_exactly_48_hours_after_now_is_urgent(fixed_now):
    deadline = fixed_now + timedelta(hours=48)

    assert deadline_status(deadline, fixed_now) == (False, True)


def test_deadline_one_microsecond_after_48_hours_is_not_urgent(fixed_now):
    deadline = fixed_now + timedelta(hours=48, microseconds=1)

    assert deadline_status(deadline, fixed_now) == (False, False)


def test_deadline_before_now_is_overdue_not_urgent(fixed_now):
    deadline = fixed_now - timedelta(microseconds=1)

    assert deadline_status(deadline, fixed_now) == (True, False)


@pytest.mark.parametrize(
    "deadline_delta",
    [timedelta(days=-1), timedelta(hours=1)],
    ids=["overdue", "upcoming"],
)
def test_completed_task_is_neither_overdue_nor_urgent(fixed_now, deadline_delta):
    deadline = fixed_now + deadline_delta

    assert deadline_status(deadline, fixed_now, completed=True) == (False, False)
