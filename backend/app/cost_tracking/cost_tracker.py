
from datetime import datetime, timezone
from typing import Any


class CostTracker:

    def create_usage_record(
        self,
        response: Any,
        provider: str,
    ) -> dict[str, Any]:
        """
        Extract token usage and cost information
        from a LiteLLM response.
        """

        usage = getattr(response, "usage", None)

        prompt_tokens = (
            getattr(usage, "prompt_tokens", 0) or 0
            if usage else 0
        )

        completion_tokens = (
            getattr(usage, "completion_tokens", 0) or 0
            if usage else 0
        )

        total_tokens = (
            getattr(usage, "total_tokens", 0) or 0
            if usage else 0
        )

        model = getattr(response, "model", None)

        # Local Ollama inference has no provider API charge.
        if provider == "ollama":
            estimated_cost = 0.0

        else:
            response_cost = getattr(
                response,
                "_hidden_params",
                {},
            )

            estimated_cost = response_cost.get(
                "response_cost",
                0.0,
            ) or 0.0

        return {
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": float(estimated_cost),
            "created_at": datetime.now(timezone.utc),
        }
