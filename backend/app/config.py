from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/researchflow"
    llm_provider: str = "openai"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    tavily_api_key: str = ""
    model_name: str = "gpt-4.1-mini"
    search_provider: str = "tavily"
    search_max_results: int = 5
    tavily_search_depth: str = "advanced"
    provider_timeout_seconds: float = 45.0
    worker_poll_interval: float = 2.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
