from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    data_dir: str = "./data"
    job_queue_key: str = "jobs:queue"
    queue_timeout_seconds: int = 2


settings = Settings()
