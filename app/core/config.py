from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings.model_validate({})
