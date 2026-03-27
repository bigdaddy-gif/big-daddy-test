from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Security
    jwt_secret: str = "dev-secret-change-me"
    jwt_issuer: str = "clawbot-setup-pro"
    access_token_ttl_minutes: int = 15

    # DB
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/clawbot"

    # Magic link
    app_base_url: str = "http://localhost:3000"  # where links should land (mobile deep link later)
    magic_link_ttl_minutes: int = 15

    # Resend
    resend_api_key: str | None = None
    resend_from_email: str = "ClawBot Setup Pro <onboarding@resend.dev>"


settings = Settings()
