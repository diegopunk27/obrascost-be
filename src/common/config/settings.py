from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    port: int = Field(default=4000, description="HTTP port")
    testing: bool = Field(default=False, description="Skip DB engine when running tests")

    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_database: str = "app_dev"
    database_url: str | None = Field(
        default=None,
        description=(
            "Full DSN. If set, overrides DB_* vars. "
            "Used by managed providers (Neon, Render, Supabase)."
        ),
    )
    sqlmodel_sync: bool = False

    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed origins for CORS.",
    )

    jwt_secret: str = "change_me_in_production"
    jwt_issuer: str = "app"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    ai_api_base_url: str = "http://localhost:8080"

    log_level: str = "INFO"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_async(self) -> str:
        # If a managed provider gave us a full DSN, normalize it for asyncpg
        if self.database_url:
            url = self.database_url
            # Neon/Render usually return postgres:// or postgresql:// — convert to async dialect
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            # asyncpg uses 'ssl=require', not 'sslmode=require'
            url = url.replace("sslmode=require", "ssl=require")
            return url
        return (
            f"postgresql+asyncpg://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_database}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
