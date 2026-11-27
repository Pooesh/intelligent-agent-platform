
from app.llm.llm_service import LLMService


class GeneralAgent:

    def __init__(self):
        self.llm_service = LLMService()

    async def process(self, user_query: str) -> str:

        prompt = f"""
        You are a helpful General Assistant Agent.

        Your responsibility is to:
        - Answer general knowledge questions.
        - Explain technical and non-technical concepts.
        - Provide clear and simple explanations.
        - Give practical examples when useful.
        - Organize complex answers into understandable sections.

        User query:
        {user_query}

        Provide a clear, accurate, and helpful response.
        """

        response = await self.llm_service.generate_response(
            message=prompt,
            provider="ollama",
            agent_name="general",
        )

        return response
