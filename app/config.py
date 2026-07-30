from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Keys
    API_KEY: str
    ENCRYPTION_KEY: str

    # BD
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # Docker Mailserver
    MAILSERVER_CONTAINER: str = "mailserver"
    IMAP_HOST: str
    IMAP_PORT: int = 993

    # WebInterface
    SESSION_COOKIE_NAME: str = "session"
    SESSION_TTL_MINUTES: int = 120
    SESSION_COOKIE_SECURE: bool = True
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
