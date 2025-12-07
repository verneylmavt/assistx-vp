# app/main.py: FastAPI app


# FastAPI main module
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models.api import (
    ChatRequest,
    ChatResponse,
    BookRequest,
    BookResponse,
    PreferencesResponse,
    PreferencesUpdateRequest,
)
from .models.domain import BookingRequest
from .services.preferences import (
    get_user_preferences,
    update_user_preferences,
)
from .services.sessions import (
    attach_plan_to_session,
    get_latest_plan_for_session,
)
from .services.bookings import perform_booking
from .storage.in_memory import (
    get_or_create_session,
)
from .agent.vacation_agent import run_vacation_agent

settings = get_settings()

app = FastAPI(
    title="Vacation Planner",
    version="0.1.0",
    description="FastAPI + Pydantic + PydanticAI + OpenAI GPT-5 Nano",
)

# Allow local dev frontend (Streamlit or other) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in real deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "model": settings.openai_model_name}


@app.get("/api/preferences/{user_id}", response_model=PreferencesResponse)
async def get_preferences(user_id: str) -> PreferencesResponse:
    prefs = get_user_preferences(user_id)
    return PreferencesResponse(preferences=prefs)


@app.put("/api/preferences/{user_id}", response_model=PreferencesResponse)
async def update_preferences(
    user_id: str, payload: PreferencesUpdateRequest
) -> PreferencesResponse:
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    prefs = update_user_preferences(user_id, data)
    return PreferencesResponse(preferences=prefs)


# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main entrypoint for the AI agent.

    The frontend sends the user's message and session; the backend:
    - loads current plan (if any),
    - runs the PydanticAI agent,
    - stores updated plan if present,
    - returns assistant message and plan snapshot.
    """
    # ensure session exists
    get_or_create_session(request.session_id, request.user_id)

    current_plan = get_latest_plan_for_session(
        session_id=request.session_id,
        user_id=request.user_id,
    )

    agent_output = await run_vacation_agent(
        user_message=request.message,
        user_id=request.user_id,
        allow_booking=request.allow_booking,
        current_plan=current_plan,
    )

    updated_plan_id = None
    if agent_output.updated_plan is not None:
        updated_plan_id = attach_plan_to_session(
            session_id=request.session_id,
            user_id=request.user_id,
            plan=agent_output.updated_plan,
        )

    # For now we don't expose plan_id to the client; the backend tracks it.
    return ChatResponse(
        session_id=request.session_id,
        user_id=request.user_id,
        assistant_message=agent_output.assistant_message,
        plan=agent_output.updated_plan,
        ask_for_booking_confirmation=agent_output.ask_for_booking_confirmation,
    )


# Booking endpoint
@app.post("/api/book", response_model=BookResponse)
async def book_trip(request: BookRequest) -> BookResponse:
    """
    Confirm a booking for the latest plan in this session.
    This endpoint should only be called after the user has explicitly confirmed.
    """
    session_state = get_or_create_session(request.session_id, request.user_id)
    if not session_state.last_plan_id:
        raise HTTPException(
            status_code=400, detail="No plan available to book in this session."
        )

    booking_request = BookingRequest(
        user_id=request.user_id,
        session_id=request.session_id,
        payment_token=request.payment_token,
        plan_id=session_state.last_plan_id,
    )

    try:
        confirmation = perform_booking(booking_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return BookResponse(
        session_id=request.session_id,
        user_id=request.user_id,
        confirmation=confirmation,
    )