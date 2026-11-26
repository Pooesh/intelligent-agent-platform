
import re
from decimal import Decimal, InvalidOperation

from app.llm.llm_service import LLMService


class MathAgent:

    def __init__(self):
        self.llm_service = LLMService()

    async def process(self, user_query: str) -> str:

        percentage_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:percent|%)\s+of\s+"
            r"(-?\d+(?:\.\d+)?)",
            user_query,
            re.IGNORECASE,
        )

        if percentage_match:
            try:
                percentage = Decimal(percentage_match.group(1))
                number = Decimal(percentage_match.group(2))

                result = (percentage / Decimal("100")) * number

                if number != 0:
                    verified_percentage = (
                        result / number * Decimal("100")
                    )

                    if verified_percentage != percentage:
                        raise ArithmeticError(
                            "Percentage verification failed."
                        )

                    verification = (
                        f"({result} / {number}) * 100 = "
                        f"{verified_percentage}%"
                    )

                else:
                    verified_result = (
                        percentage / Decimal("100")
                    ) * number

                    if verified_result != result:
                        raise ArithmeticError(
                            "Zero-value verification failed."
                        )

                    verification = (
                        f"({percentage} / 100) * {number} "
                        f"= {verified_result}"
                    )

                return (
                    f"Formula:\n"
                    f"({percentage} / 100) * {number}\n\n"
                    f"Calculation:\n"
                    f"{percentage / Decimal('100')} * "
                    f"{number} = {result}\n\n"
                    f"Independent verification:\n"
                    f"{verification}\n\n"
                    f"Final answer: {result}"
                )

            except (InvalidOperation, ArithmeticError):
                pass

        prompt = f"""
        You are a careful and reliable Mathematical Reasoning Agent.

        Solve mathematical problems accurately.

        Follow these rules:
        1. Understand the question.
        2. Identify given values and required results.
        3. Select the appropriate formula.
        4. Substitute values and calculate carefully.
        5. Independently verify the result.
        6. If calculations disagree, recalculate.
        7. Never invent verification results.
        8. Clearly distinguish intermediate values from
           the final answer.

        Pay special attention to percentages, decimals,
        division, negative numbers and order of operations.

        Provide:
        - Formula
        - Step-by-step calculation
        - Independent verification
        - Clearly identified final answer

        User query:
        {user_query}

        Be accurate, concise and transparent.
        """

        response = await self.llm_service.generate_response(
            message=prompt,
            provider="ollama",
        )

        return response
