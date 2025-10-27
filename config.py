import os
from pydantic import BaseModel, PostgresDsn, RedisDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


class SMTPConfig(BaseModel):
    server: str = os.getenv("EMAIL_HOST", "smtp_server")
    port: int = os.getenv("EMAIL_PORT", 587)
    username: str = os.getenv("EMAIL_HOST_USER", "smtp_user")
    password: str = os.getenv("EMAIL_HOST_PASSWORD", "smtp_password")
    template_path: str = os.getenv("EMAIL_TEMPLATE_PATH", "templates")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expire: int = os.getenv("JWT_EXPIRE")
    smtp: SMTPConfig = SMTPConfig()

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: str

    JWT_ALGORITHM: str
    JWT_EXPIRE: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str

    @computed_field
    @property
    def redis_url(self) -> RedisDsn:
        return MultiHostUrl.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=self.REDIS_DB,
        )

    @computed_field
    @property
    def asyncpg_url(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def postgres_url(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgres",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            path=self.POSTGRES_DB,
        )


settings = Settings()
