from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentTypes(Enum):
    development = "development"
    testing = "testing"
    production = "production"


class Settings(BaseSettings):
    ENVIRONMENT: EnvironmentTypes
    DEBUG: bool = False
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    BOT_TOKEN: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    MONGO_HOST: str
    MONGO_PORT: int

    MEDIA_PATH: Path = BASE_DIR / "media"

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    DEFAULT_RATING: int = 1400

    # App settings
    REWIND_LIMIT: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings.model_validate({})
