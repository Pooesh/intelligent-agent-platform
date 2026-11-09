from litellm import acompletion

from app.llm.model_config import (
    DEFAULT_PROVIDER,
    OLLAMA_MODEL,
    OLLAMA_API_BASE,
    OPENAI_MODEL,
)


class LLMService:

    async def generate_response(
        self,
        message: str,
        provider: str = DEFAULT_PROVIDER,
    ) -> str:

        if provider == "ollama":
            model = OLLAMA_MODEL
            api_base = OLLAMA_API_BASE

        elif provider == "openai":
            model = OPENAI_MODEL
            api_base = None

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        response = await acompletion(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            api_base=api_base,
        )

        return response.choices[0].message.content
