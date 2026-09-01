from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Config
    GEMINI_API_KEY: str = ""
    DEFAULT_MODEL: str = "gemini/gemini-1.5-flash" # LiteLLM format
    OLLAMA_API_BASE: str = "http://localhost:11434"
    
    # Database & Cache
    DATABASE_URL: str = "postgresql://user:pass@neon.tech/dbname"
    REDIS_URL: str = "redis://default:pass@upstash.redis.com:6379"
    
    # Observability
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
