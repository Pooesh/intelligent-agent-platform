
from app.llm.llm_service import LLMService


class MathAgent:

    def __init__(self):
        self.llm_service = LLMService()

    async def process(self, user_query: str) -> str:

        prompt = f"""
        You are a specialized Math Agent.

        Your responsibility is to:
        - Solve mathematical problems.
        - Perform calculations carefully.
        - Explain the solution step by step.
        - Show formulas when appropriate.
        - Verify your calculations before answering.

        User query:
        {user_query}

        Provide an accurate mathematical response.
        """

        response = await self.llm_service.generate_response(
            message=prompt,
            provider="ollama",
        )

        return response
