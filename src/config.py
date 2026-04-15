import os

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env="postgres_url")
    main_service_url: str = Field(env="main_service_url")
    main_service_timeout_seconds: float = Field(default=5.0, env="main_service_timeout_seconds")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
