from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenAI API
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # Database
    database_url: str = "sqlite+aiosqlite:///./skin_analysis.db"

    # Image
    max_image_size_mb: int = 5
    allowed_image_types: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # API key auth for mobile client
    api_secret_key: str

    # JWT
    jwt_secret_key: str = "change-me-to-a-long-random-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7일


settings = Settings()  # type: ignore[call-arg]
