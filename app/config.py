# app/config.py
from __future__ import annotations

import os
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseModel):
    app_env: str = "dev"
    openai_model_name: str = "gpt-5-nano"
    openai_api_key: str = ""
    
    class Config:
        frozen = True


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "dev"),
        openai_model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-5-nano"),
        openai_api_key=os.getenv("OPENAI_API_KEY", None),
    )