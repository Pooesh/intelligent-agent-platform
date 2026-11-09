from app.core.config import settings


# Default LLM provider
DEFAULT_PROVIDER = "ollama"

# Ollama model configuration
OLLAMA_MODEL = "ollama_chat/qwen2.5-coder:1.5b"
OLLAMA_API_BASE = settings.ollama_base_url

# OpenAI model configuration (to be enabled later)
OPENAI_MODEL = "gpt-4.1"
