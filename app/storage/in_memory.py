# app/storage/in_memory.py: In-memory storage
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel

from ..models.domain import (
    UserPreferences,
    CalendarEvent,
    VacationPlan,
    BookingConfirmation,
)


class SessionState(BaseModel):
    session_id: str
    user_id: str
    last_plan_id: Optional[str] = None


# In-memory "databases"
PREFERENCES: Dict[str, UserPreferences] = {}
CALENDAR_EVENTS: Dict[str, List[CalendarEvent]] = {}
PLANS: Dict[str, VacationPlan] = {}
BOOKINGS: Dict[str, BookingConfirmation] = {}
SESSIONS: Dict[str, SessionState] = {}


def get_or_create_session(session_id: str, user_id: str) -> SessionState:
    existing = SESSIONS.get(session_id)
    if existing:
        return existing
    state = SessionState(session_id=session_id, user_id=user_id)
    SESSIONS[session_id] = state
    return state


def save_plan(plan: VacationPlan) -> str:
    plan_id = str(uuid4())
    PLANS[plan_id] = plan
    return plan_id


def get_plan(plan_id: str) -> VacationPlan:
    return PLANS[plan_id]


def save_booking(
    user_id: str, session_id: str, plan_id: str, total: float, currency: str
) -> BookingConfirmation:
    booking_id = str(uuid4())
    confirmation = BookingConfirmation(
        booking_id=booking_id,
        user_id=user_id,
        session_id=session_id,
        plan_id=plan_id,
        flight_confirmation_code=f"FL-{booking_id[:8].upper()}",
        hotel_confirmation_code=f"HT-{booking_id[8:16].upper()}",
        total_charged=total,
        currency=currency,
        created_at=datetime.utcnow(),
    )
    BOOKINGS[booking_id] = confirmation
    return confirmation


def get_or_create_preferences(user_id: str) -> UserPreferences:
    prefs = PREFERENCES.get(user_id)
    if prefs:
        return prefs
    prefs = UserPreferences(
        user_id=user_id,
        home_city="SIN",
        default_currency="USD",
        interests=["food", "museums"],
        travel_style="balanced",
    )
    PREFERENCES[user_id] = prefs
    return prefs


def update_preferences(user_id: str, update: dict) -> UserPreferences:
    prefs = get_or_create_preferences(user_id)
    updated = prefs.model_copy(update=update, deep=True)
    PREFERENCES[user_id] = updated
    return updated


def get_calendar_events(user_id: str) -> List[CalendarEvent]:
    return CALENDAR_EVENTS.get(user_id, [])


def set_calendar_events(user_id: str, events: List[CalendarEvent]) -> None:
    CALENDAR_EVENTS[user_id] = events