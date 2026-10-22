from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = Field(min_length=32)
    # За nginx фронт и API на одном домене, CORS не нужен (пустая строка в env).
    # Значение по умолчанию оставлено для `npm run dev` на порту 3000.
    # В env: список через запятую, например "https://a.kz,https://b.kz".
    CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    # Swagger (/docs, /openapi.json). На публичном сервере выключить.
    DOCS_ENABLED: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


settings = Settings()
