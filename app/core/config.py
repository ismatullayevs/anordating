from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    DEBUG: bool = False
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    BOT_TOKEN: str
    
    DATABASE_URL: str
    MEDIA_PATH: Path = BASE_DIR / "media"

    DEFAULT_RATING: int = 1400

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings.model_validate({})
