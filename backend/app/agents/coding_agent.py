
from app.llm.llm_service import LLMService


class CodingAgent:

    def __init__(self):
        self.llm_service = LLMService()

    async def process(self, user_query: str) -> str:

        prompt = f"""
        You are a specialized Coding Agent.

        Your responsibility is to:
        - Generate clean and readable code.
        - Explain programming concepts.
        - Follow programming best practices.
        - Provide examples when useful.

        User query:
        {user_query}

        Provide a helpful programming response.
        """

        response = await self.llm_service.generate_response(
            message=prompt,
            provider="ollama",
        )

        return response
