
import re

from app.llm.llm_service import LLMService


class SupervisorAgent:

    def __init__(self):
        self.llm_service = LLMService()

    async def classify_query(self, user_query: str) -> str:

        query = user_query.lower().strip()

        # 1. Detect clear coding requests
        coding_keywords = [
            "write code",
            "write a program",
            "generate code",
            "implement",
            "debug",
            "fix this code",
            "fix my code",
            "refactor",
            "review my code",
            "optimize my code",
            "create a class",
            "create a function",
            "build an application",
            "java stream api",
            "programming syntax",
            "data structure implementation",
        ]

        if any(keyword in query for keyword in coding_keywords):
            return "coding"

        # 2. Detect clear mathematical requests
        math_keywords = [
            "calculate",
            "solve equation",
            "solve this equation",
            "calculate percentage",
            "what is the percentage",
            "square root",
            "differentiate",
            "integrate",
            "arithmetic",
        ]

        if any(keyword in query for keyword in math_keywords):
            return "math"

        # Detect basic arithmetic expressions
        if re.search(r"\d+\s*[+\-*/]\s*\d+", query):
            return "math"

        # 3. Detect explicit research and technology evaluation requests
        research_keywords = [
            "compare",
            "comparison",
            "advantages and disadvantages",
            "pros and cons",
            "architecture of",
            "architecture",
            "research",
            "investigate",
            "evaluate",
            "technical analysis",
            "use cases",
            "technology trends",
            "which framework",
            "which technology",
            "which platform",
            "features of",
        ]

        if any(keyword in query for keyword in research_keywords):
            return "research"

        # 4. Detect general knowledge and everyday questions
        general_keywords = [
            "benefits of",
            "what are the benefits",
            "importance of",
            "meaning of",
            "what is",
            "who is",
            "how does",
            "why is",
            "explain the difference between",
            "explain the differences between",
            "difference between",
            "differences between",
            "explain",
        ]

        if any(keyword in query for keyword in general_keywords):
            return "general"

        # 5. Use the LLM for ambiguous queries
        prompt = f"""
        You are the Supervisor Agent of an AI Intelligent Platform.

        Classify the user query into exactly one category:

        coding:
        Writing, debugging or implementing code.

        math:
        Mathematical calculations, equations and problems.

        research:
        Investigating topics, comparing technologies,
        analyzing architectures and evaluating tools.

        general:
        Everyday questions, definitions and simple explanations.

        Examples:

        Query: Write a Java program to reverse a string.
        Category: coding

        Query: Compare LangGraph, CrewAI and AutoGen.
        Category: research

        Query: Explain Spring Boot architecture.
        Category: research

        Query: Calculate 25 percent of 800.
        Category: math

        Query: What is cloud computing?
        Category: general

        Query: Explain the difference between AI and machine learning.
        Category: general

        USER QUERY:
        {user_query}

        Return ONLY one word:
        coding, math, research, or general.
        """

        result = await self.llm_service.generate_response(
            message=prompt,
            provider="ollama",
            agent_name="supervisor",
        )

        category = result.strip().lower()

        if category not in {"coding", "math", "research", "general"}:
            return "general"

        return category
