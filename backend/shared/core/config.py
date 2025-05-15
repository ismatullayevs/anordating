from enum import Enum
from pathlib import Path
from urllib.parse import quote_plus

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
    MONGO_PORT: int | None = None
    MONGO_ADMIN: str
    MONGO_PASSWORD: str

    MEDIA_PATH: Path = BASE_DIR / "media"
    DOMAIN: str

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def mongo_url(self):
        admin = quote_plus(self.MONGO_ADMIN)
        password = quote_plus(self.MONGO_PASSWORD)
        if self.ENVIRONMENT == EnvironmentTypes.production:
            return f"mongodb+srv://{admin}:{password}@{self.MONGO_HOST}/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
        return f"mongodb://{admin}:{password}@{self.MONGO_HOST}:{self.MONGO_PORT}"

    # App settings
    REWIND_LIMIT: int = 5
    DEFAULT_RATING: int = 1400

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings.model_validate({})
