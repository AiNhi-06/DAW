from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/tuyen_sinh_qnu"
    api_url: str = "http://127.0.0.1:8000"
    upload_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
UPLOAD_DIR = BASE_DIR / settings.upload_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
