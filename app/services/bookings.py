# app/services/bookings.py: Booking service
from __future__ import annotations

from ..models.domain import BookingRequest, BookingConfirmation
from ..storage.in_memory import (
    get_plan,
    save_booking,
    get_or_create_session,
)


def perform_booking(request: BookingRequest) -> BookingConfirmation:
    """
    Core booking logic.

    In a real system, this would:
    - validate payment_token with a payment provider,
    - call airline/hotel booking APIs,
    - handle partial failures and rollbacks.
    For PoC we just record a booking and synthesize confirmation codes.
    """
    session_state = get_or_create_session(request.session_id, request.user_id)
    plan = get_plan(request.plan_id)

    # Basic sanity check: plan belongs to the same user
    if plan.user_id != request.user_id:
        raise ValueError("Plan does not belong to this user")

    total = plan.estimated_total_cost
    currency = plan.currency

    confirmation = save_booking(
        user_id=request.user_id,
        session_id=request.session_id,
        plan_id=request.plan_id,
        total=total,
        currency=currency,
    )
    return confirmation
