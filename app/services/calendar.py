# app/services/calendar.py: Calendar service
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List

from ..models.domain import CalendarEvent, DateRange
from ..storage.in_memory import get_calendar_events, set_calendar_events


def seed_mock_calendar(user_id: str) -> None:
    """
    Optionally pre-populate some busy times for demonstration.
    """
    if get_calendar_events(user_id):
        return

    today = date.today()
    events = [
        CalendarEvent(
            user_id=user_id,
            title="Work",
            start=datetime.combine(today + timedelta(days=3), datetime.min.time()),
            end=datetime.combine(today + timedelta(days=3), datetime.max.time()),
            all_day=True,
        )
    ]
    set_calendar_events(user_id, events)


def find_free_date_ranges(
    user_id: str, trip_duration_days: int, window_days: int = 60
) -> List[DateRange]:
    """
    Very naive algorithm: mark days as busy if any event overlaps, then find
    contiguous free blocks at least `trip_duration_days` long within the next `window_days`.
    """
    seed_mock_calendar(user_id)
    busy_events = get_calendar_events(user_id)

    today = date.today()
    busy_days = set()
    for e in busy_events:
        d = e.start.date()
        while d <= e.end.date():
            busy_days.add(d)
            d += timedelta(days=1)

    free_ranges: List[DateRange] = []
    start = None

    for offset in range(window_days):
        d = today + offset * timedelta(days=1)
        if d in busy_days:
            if start is not None:
                # end the current free streak
                if (d - start).days >= trip_duration_days:
                    free_ranges.append(DateRange(start=start, end=d - timedelta(days=1)))
                start = None
        else:
            if start is None:
                start = d

    # tail
    if start is not None:
        d = today + timedelta(days=window_days)
        if (d - start).days >= trip_duration_days:
            free_ranges.append(DateRange(start=start, end=d - timedelta(days=1)))

    return free_ranges
