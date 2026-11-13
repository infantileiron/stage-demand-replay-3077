import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:////tmp/stage-demand.sqlite3")
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    jwt_secret: str = os.getenv("JWT_SECRET", "local-demo-change-me-32-characters-long")
    seed_demo: bool = os.getenv("SEED_DEMO", "false").lower() == "true"
    artifacts: str = os.getenv("ARTIFACTS_DIR", "/app/artifacts")

settings = Settings()
