# app/models/domain.py: Domain models
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    user_id: str
    home_city: str = Field(..., description="Home city or airport code, e.g. 'SIN'")
    default_currency: str = "USD"
    max_budget_total: Optional[float] = Field(
        None, description="Max total budget for the whole trip, in default_currency"
    )
    max_budget_per_day: Optional[float] = Field(
        None, description="Max budget per day, in default_currency"
    )
    interests: List[str] = Field(
        default_factory=list,
        description="High-level interests like 'food', 'museums', 'nature'",
    )
    travel_style: str = Field(
        "balanced", description="e.g. 'relaxed', 'packed', 'balanced'"
    )
    preferred_airlines: List[str] = Field(default_factory=list)
    preferred_hotel_types: List[str] = Field(
        default_factory=list, description="e.g. 'budget', 'midrange', 'luxury'"
    )


class CalendarEvent(BaseModel):
    user_id: str
    title: str
    start: datetime
    end: datetime
    all_day: bool = False


class DateRange(BaseModel):
    start: date
    end: date


class FlightOption(BaseModel):
    id: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    airline: str
    cabin_class: str = "economy"
    price: float
    currency: str = "USD"


class HotelOption(BaseModel):
    id: str
    destination_city: str
    name: str
    check_in: date
    check_out: date
    price_per_night: float
    total_price: float
    currency: str = "USD"
    rating: float = 4.0


class DayPlan(BaseModel):
    date: date
    morning: str
    afternoon: str
    evening: str
    notes: Optional[str] = None


class VacationPlan(BaseModel):
    user_id: str
    destination_city: str
    start_date: date
    end_date: date
    flight: FlightOption
    hotel: HotelOption
    daily_plans: List[DayPlan]
    estimated_total_cost: float
    currency: str = "USD"
    status: str = Field(
        "planned", description="planned | booked | cancelled (for future extensions)"
    )


class BookingRequest(BaseModel):
    user_id: str
    session_id: str
    payment_token: str  # opaque token (never raw card number)
    plan_id: str        # reference to a stored VacationPlan


class BookingConfirmation(BaseModel):
    booking_id: str
    user_id: str
    session_id: str
    plan_id: str
    flight_confirmation_code: str
    hotel_confirmation_code: str
    total_charged: float
    currency: str
    created_at: datetime