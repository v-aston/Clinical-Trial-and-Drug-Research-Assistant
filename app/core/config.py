from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Research Assistant"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    gemini_api_key: str
    # embedding_model: str = "gemini-embedding-001"
    # embedding_dim: int = 768

    groq_api_key: str | None = None
    groq_model: str = "llama3-8b-8192"
    groq_max_tokens: int = 250
    llm_backend: str = "groq"

    pubmed_email: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()
