from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./hyperlocal.db"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200

    # Google OAuth2 — set these in .env / Render environment variables
    google_client_id: str = ""
    google_client_secret: str = ""

    # Public URL of this backend (used to build the Google callback URL)
    app_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
