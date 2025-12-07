# app/models/api.py: API models
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field
from .domain import VacationPlan, BookingConfirmation, UserPreferences


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Client-side session identifier")
    user_id: str
    message: str
    allow_booking: bool = Field(
        False, description="Whether the user allows booking actions in this session"
    )


class ChatResponse(BaseModel):
    session_id: str
    user_id: str
    assistant_message: str
    plan: Optional[VacationPlan] = None
    ask_for_booking_confirmation: bool = False


class BookRequest(BaseModel):
    session_id: str
    user_id: str
    payment_token: str = Field(
        ..., description="Opaque payment token, never raw card data"
    )


class BookResponse(BaseModel):
    session_id: str
    user_id: str
    confirmation: BookingConfirmation


class PreferencesResponse(BaseModel):
    preferences: UserPreferences


class PreferencesUpdateRequest(BaseModel):
    home_city: Optional[str] = None
    default_currency: Optional[str] = None
    max_budget_total: Optional[float] = None
    max_budget_per_day: Optional[float] = None
    interests: Optional[List[str]] = None
    travel_style: Optional[str] = None
    preferred_airlines: Optional[List[str]] = None
    preferred_hotel_types: Optional[List[str]] = None