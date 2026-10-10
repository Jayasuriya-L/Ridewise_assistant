import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
WORKSPACE_RESOURCES = PROJECT_ROOT / "hackathon_resources"

class Settings(BaseSettings):
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # Database
    DATABASE_PATH: str = str(WORKSPACE_RESOURCES / "ridewise.db")

    # Policy files
    POLICY_DIR: str = str(WORKSPACE_RESOURCES)

    # NeoStats OpenAI LLM Endpoint
    OPENAI_ENDPOINT: str = "https://neo-hackathon.services.ai.azure.com/openai/v1/"
    OPENAI_MODEL_NAME: str = "gpt-oss-120b"
    OPENAI_DEPLOYMENT_NAME: str = "Neo-Hackathon"
    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=[
            str(BASE_DIR / ".env"),
            str(PROJECT_ROOT / ".env"),
        ],
        extra="ignore"
    )

settings = Settings()

# Validation helper
def get_verified_db_path() -> str:
    path = Path(settings.DATABASE_PATH)
    if not path.is_file():
        alt = WORKSPACE_RESOURCES / "ridewise.db"
        if alt.is_file():
            return str(alt)
    return str(path)
