from deepeval.models import OllamaModel

from app.core.config import settings


# General-purpose local Ollama model used for evaluation
EVALUATION_MODEL_NAME = "llama3:latest"


def get_judge_model() -> OllamaModel:
    """
    Create and return the DeepEval evaluation judge.

    Uses the general-purpose Llama 3 model
    running on the local Ollama server.
    """

    return OllamaModel(
        model=EVALUATION_MODEL_NAME,
        base_url=settings.ollama_base_url,
        temperature=0,
    )