
import os

import litellm
from litellm import acompletion

from app.core.config import settings
from app.llm.model_config import (
    DEFAULT_PROVIDER,
    OLLAMA_MODEL,
    OLLAMA_API_BASE,
    OPENAI_MODEL,
)
from app.cost_tracking.cost_tracker import CostTracker
from app.cost_tracking.cost_repository import CostRepository


# Configure Langfuse credentials.
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
os.environ["LANGFUSE_HOST"] = settings.langfuse_base_url


# Configure direct Langfuse SDK callbacks.
if settings.langfuse_public_key and settings.langfuse_secret_key:
    litellm.success_callback = ["langfuse"]
    litellm.failure_callback = ["langfuse"]


class LLMService:

    def __init__(self):
        self.llm_service_name = "intelligent-agent-platform"
        self.cost_tracker = CostTracker()
        self.cost_repository = CostRepository()

    async def generate_response(
        self,
        message: str,
        provider: str = DEFAULT_PROVIDER,
        agent_name: str = "unknown",
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
            metadata={
                "service": self.llm_service_name,
                "environment": settings.environment,
                "agent_name": agent_name,
            },
        )

        # Extract token usage and cost information.
        usage_record = self.cost_tracker.create_usage_record(
            response=response,
            provider=provider,
        )

        usage_record["agent_name"] = agent_name
        usage_record["service"] = self.llm_service_name

        # Persist usage information in MongoDB.
        try:
            await self.cost_repository.save_usage(usage_record)
        except Exception as exc:
            # Usage tracking should not prevent a successful
            # LLM response from reaching the agent.
            print(f"Warning: Could not save LLM usage: {exc}")

        return response.choices[0].message.content
