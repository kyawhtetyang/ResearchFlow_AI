from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/researchflow"
    openai_api_key: str = ""
    worker_poll_interval: float = 2.0

    class Config:
        env_file = ".env"

settings = Settings()
