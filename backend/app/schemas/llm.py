from typing import Literal

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The message or prompt sent to the LLM",
    )

    provider: Literal["ollama", "openai"] = Field(
        default="ollama",
        description="The LLM provider to use",
    )


class LLMResponse(BaseModel):
    provider: str
    response: str
