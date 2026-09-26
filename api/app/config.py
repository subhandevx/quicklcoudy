from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    data_dir: str = "./data"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    max_upload_bytes: int = 10 * 1024 * 1024
    job_queue_key: str = "jobs:queue"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
