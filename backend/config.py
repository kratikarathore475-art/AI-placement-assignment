from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent  # project root (AI-Placement-Assistant/)


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/placement_assistant.db"

    LLM_PROVIDER: str = "groq"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    VECTOR_STORE_PATH: str = "./vector_store/placement_index.faiss"
    VECTOR_METADATA_PATH: str = "./vector_store/placement_metadata.json"

    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()