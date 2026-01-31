from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Agentic Web Factory"
    debug: bool = False

    # API Configuration
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # GitHub
    github_token: str = ""
    github_org: str = ""

    # Claude Code CLI (default to common install locations)
    claude_cli_path: str = "/usr/bin/claude"

    # Agent Configuration
    agent_logs_dir: str = ".agent_logs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
