from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    API_URL: str = "https://api.example.com"
    INTERNAL_TOKEN: str = ""
    REWIND_LIMIT: int = 5


settings = Settings()
