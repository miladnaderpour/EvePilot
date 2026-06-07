"""Configuration loading for EvePilot."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and .env files."""

    app_name: str = Field("EvePilot", validation_alias="EVEPILOT_APP_NAME")
    app_env: str = Field("dev", validation_alias="EVEPILOT_APP_ENV")
    log_level: str = Field("INFO", validation_alias="EVEPILOT_LOG_LEVEL")
    log_format: str = Field("json", validation_alias="EVEPILOT_LOG_FORMAT")
    log_output: str = Field("stdout", validation_alias="EVEPILOT_LOG_OUTPUT")
    log_file_path: str = Field(
        "logs/evepilot.log",
        validation_alias="EVEPILOT_LOG_FILE_PATH",
    )
    log_targets_json: str | None = Field(
        None,
        validation_alias="EVEPILOT_LOG_TARGETS_JSON",
    )

    eve_ng_url: str = Field(validation_alias="EVEPILOT_EVE_NG_URL")
    eve_ng_username: str = Field(validation_alias="EVEPILOT_EVE_NG_USERNAME")
    eve_ng_password: SecretStr = Field(validation_alias="EVEPILOT_EVE_NG_PASSWORD")
    eve_ng_verify_ssl: bool = Field(
        False,
        validation_alias="EVEPILOT_EVE_NG_VERIFY_SSL",
    )
    eve_ng_timeout_seconds: float = Field(
        10.0,
        validation_alias="EVEPILOT_EVE_NG_TIMEOUT_SECONDS",
    )

    model_config = SettingsConfigDict(
        env_prefix="EVEPILOT_",
        env_file=".env",
        case_sensitive=True,
        populate_by_name=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached EvePilot settings."""

    return Settings()
