from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    WORKERS_COUNT: int = 1
    HOST: str = "localhost"
    PORT: int = 8900
    RELOAD: bool = True
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    API_PREFIX: str
    DB_ECHO: bool = False
    THUMBNAIL_WIDTH: int = 500
    THUMBNAIL_HEIGHT: int = 500
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int
    EMAIL_TOKEN_SALT: str
    EMAIL_EXPIRE_SECONDS: int = 600

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def DB_SYNC_URL(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
