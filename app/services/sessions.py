# app/services/sessions.py: Sessions helper
from __future__ import annotations

from typing import Optional

from ..models.domain import VacationPlan
from ..storage.in_memory import get_or_create_session, save_plan, PLANS


def attach_plan_to_session(
    session_id: str, user_id: str, plan: VacationPlan
) -> str:
    """
    Store plan and link it to the session.
    """
    session = get_or_create_session(session_id, user_id)
    plan_id = save_plan(plan)
    session.last_plan_id = plan_id
    return plan_id


def get_latest_plan_for_session(
    session_id: str, user_id: str
) -> Optional[VacationPlan]:
    session = get_or_create_session(session_id, user_id)
    if not session.last_plan_id:
        return None
    return PLANS.get(session.last_plan_id)