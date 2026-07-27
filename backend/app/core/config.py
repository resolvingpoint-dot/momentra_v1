from __future__ import annotations

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Momentra API"
    app_version: str = "0.1.0"
    debug: bool = False
    # Explicit production signal (Dokploy should set MOMENTRA_ENV=production).
    momentra_env: str = Field(default="", validation_alias="MOMENTRA_ENV")

    # Firebase Admin
    firebase_credentials_path: str = ""
    firebase_service_account_json_b64: str = ""
    firebase_project_id: str = ""
    firebase_client_email: str = ""
    firebase_private_key: str = ""

    # JWT session tokens (legacy aliases)
    session_secret_key: str = Field(default="", alias="jwt_secret")
    session_algorithm: str = "HS256"
    session_expire_hours: int = 72

    # App session token (new, overrides legacy)
    app_session_secret: str = ""
    app_session_expires_minutes: int = 60

    # CORS
    cors_origins_str: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_str.split(",") if o.strip()]

    @property
    def effective_session_secret(self) -> str:
        return self.app_session_secret or self.session_secret_key

    @property
    def is_production(self) -> bool:
        """True when explicitly production or when DEBUG is off."""
        return self.momentra_env.strip().lower() == "production" or not self.debug

    # Supabase / PostgreSQL
    database_url: str = ""

    # Connection pool (SQLAlchemy async engine). Explicit, tunable values;
    # ``pool_recycle`` guards against stale connections on cloud Postgres, and
    # ``pool_pre_ping`` (set in database.py) validates connections on checkout.
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # Object storage (avatars / moment covers). When unset, upload URLs are
    # stubbed with a relative path so the contract works without a bucket.
    storage_public_base_url: str = ""
    # Optional: used to derive STORAGE_PUBLIC_BASE_URL when that is unset
    # (Dokploy often already has SUPABASE_URL from the project setup).
    supabase_url: str = ""

    @property
    def effective_storage_public_base_url(self) -> str:
        explicit = (self.storage_public_base_url or "").strip().rstrip("/")
        if explicit:
            return explicit
        base = (self.supabase_url or "").strip().rstrip("/")
        if base.startswith("https://"):
            return f"{base}/storage/v1/object/public/momentra"
        return ""

    # Base for shareable/email invite links. Defaults to the app's custom URL
    # scheme so links open the installed app directly; override with an https
    # universal/app link in production (prefer www — apex redirects break AASA).
    # e.g. https://www.momentra.tech/invite
    invite_link_base_url: str = Field(
        default="momentra://invite",
        validation_alias="MOMENTRA_APP_INVITE_BASE_URL",
    )

    # Resend (group invite email). Env already uses MOMENTRA_RESEND_*.
    resend_api_key: str = Field(default="", validation_alias="MOMENTRA_RESEND_API_KEY")
    resend_from: str = Field(
        default="",
        validation_alias="MOMENTRA_RESEND_FROM",
    )

    # Redis (optional)
    redis_url: str = ""

    # Celery (background jobs). When the dedicated URLs are unset they fall back
    # to redis_url so a single Redis instance serves cache + broker + backend.
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    celery_task_always_eager: bool = False  # run tasks inline (tests/local)
    celery_max_retries: int = 5
    celery_retry_backoff_max: int = 600

    @property
    def effective_celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def effective_celery_result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    # Rate limiting
    rate_limit_max_requests: int = 60
    rate_limit_window_seconds: int = 60

    # Acceptance / test-only auth. Both flags must be true; refused when DEBUG=false.
    allow_test_auth: bool = False
    # When set, acceptance fixtures prefer this URL over DATABASE_URL.
    acceptance_database_url: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }

    @model_validator(mode="after")
    def _require_session_secret_in_production(self) -> "Settings":
        """Fail fast when tokens would be signed with an empty secret.

        In production (``DEBUG=false``) an empty ``effective_session_secret``
        means HS256 JWTs are signed/verified with an empty key, allowing
        trivial token forgery. We refuse to boot rather than run insecurely.
        Development (``DEBUG=true``) is exempt so local/test setups need no key.
        """
        if not self.debug and not self.effective_session_secret:
            raise ValueError(
                "APP_SESSION_SECRET (or JWT_SECRET) must be set when DEBUG=false; "
                "refusing to sign JWTs with an empty secret."
            )
        if self.allow_test_auth and not self.debug:
            raise ValueError(
                "ALLOW_TEST_AUTH requires DEBUG=true; refusing to enable test login in production."
            )
        return self


def validate_production_security(cfg: Settings) -> None:
    """Refuse to boot with unsafe production configuration.

    Invoked when ``MOMENTRA_ENV=production`` or ``DEBUG=false``. Clear errors
    so Dokploy / ops can fix env without guessing.
    """
    if not cfg.is_production:
        return

    errors: list[str] = []

    if cfg.debug:
        errors.append("DEBUG must be false in production (MOMENTRA_ENV=production)")
    if cfg.allow_test_auth:
        errors.append("ALLOW_TEST_AUTH must not be enabled in production")
    # Prefer ≥64; allow ≥48 so existing Dokploy JWT_SECRET values can boot
    # while ops rotate to a longer APP_SESSION_SECRET.
    secret_len = len(cfg.effective_session_secret)
    if secret_len < 48:
        errors.append(
            "APP_SESSION_SECRET (or JWT_SECRET) must be at least 48 characters in production "
            "(64+ recommended; generate with: python -c \"import secrets; print(secrets.token_urlsafe(64))\")"
        )
    elif secret_len < 64:
        import logging

        logging.getLogger(__name__).warning(
            "APP_SESSION_SECRET/JWT_SECRET is only %s chars; rotate to ≥64 for production hardening",
            secret_len,
        )

    storage = cfg.effective_storage_public_base_url
    if not storage.startswith("https://"):
        errors.append(
            "STORAGE_PUBLIC_BASE_URL must be an https:// URL in production "
            "(or set SUPABASE_URL so it can be derived as "
            "{SUPABASE_URL}/storage/v1/object/public/momentra)"
        )

    origins = cfg.cors_origins
    if not origins:
        errors.append("CORS_ORIGINS_STR must list explicit origins in production")
    elif any(o.strip() == "*" for o in origins):
        errors.append("CORS_ORIGINS_STR must not include '*' when credentials are enabled")

    if errors:
        joined = "; ".join(errors)
        raise RuntimeError(f"Production security check failed: {joined}")


settings = Settings()
