from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    API_URL: str = "https://api.example.com"
    INTERNAL_TOKEN: str = ""


settings = Settings()
