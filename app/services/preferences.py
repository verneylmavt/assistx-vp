# app/services/preferences.py: Preferences service
from __future__ import annotations

from ..models.domain import UserPreferences
from ..storage.in_memory import get_or_create_preferences, update_preferences


def get_user_preferences(user_id: str) -> UserPreferences:
    """
    Retrieve user preferences, creating sensible defaults if they don't exist.
    """
    return get_or_create_preferences(user_id)


def update_user_preferences(user_id: str, data: dict) -> UserPreferences:
    """
    Update user preferences from partial data.
    """
    return update_preferences(user_id, data)
