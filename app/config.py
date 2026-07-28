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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
