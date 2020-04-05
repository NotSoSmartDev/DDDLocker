from pydantic import BaseSettings


class Settings(BaseSettings):
    dsn: str

    class Config:
        env_file = ".env"


settings = Settings()
