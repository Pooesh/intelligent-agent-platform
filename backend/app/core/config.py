
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application information
    app_name: str = "AI Intelligent Platform"
    app_version: str = "0.1.0"

    # API configuration
    api_v1_prefix: str = "/api/v1"

    # Environment configuration
    environment: str = "development"
    debug: bool = True

    # MongoDB configuration
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "intelligent_agent_platform"

    # Redis configuration
    redis_url: str = "redis://localhost:6379/0"

    # Ollama configuration
    ollama_base_url: str = "http://localhost:11434"

    # Tavily web search configuration
    tavily_api_key: str = ""

    # Frontend configuration
    frontend_origins: str = "http://localhost:5173"

    # Environment variable configuration
    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Create one settings object for the application
settings = Settings()
