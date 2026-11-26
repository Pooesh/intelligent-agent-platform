
import re
from decimal import Decimal, InvalidOperation

from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import SingleTurnParams

from app.evaluation.judge_model import get_judge_model


def extract_numerical_answer(text: str) -> str | None:
    """
    Extract the final numerical answer from a response.

    Priority:
    1. LaTeX boxed answer.
    2. Clearly identified final-answer section.
    3. Explicit final-answer statements.
    4. Last numerical value as a fallback.
    """

    number_pattern = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"

    # 1. Prefer a boxed mathematical answer.
    boxed_match = re.search(
        rf"\\boxed\s*\{{\s*({number_pattern})\s*\}}",
        text,
        flags=re.IGNORECASE,
    )

    if boxed_match:
        return boxed_match.group(1)

    # 2. Look for a clearly identified final-answer section.
    final_section_match = re.search(
        r"(?:clearly\s+identified\s+)?final\s+answer\s*:?\s*\**",
        text,
        flags=re.IGNORECASE,
    )

    if final_section_match:
        final_section = text[final_section_match.end():]

        # Stop at the next Markdown heading, if one exists.
        final_section = re.split(
            r"\n\s*\*\*[^*\n]+:\*\*",
            final_section,
            maxsplit=1,
        )[0]

        section_numbers = re.findall(
            number_pattern,
            final_section,
        )

        if section_numbers:
            return section_numbers[-1]

    # 3. Look for explicit final-answer statements.
    final_answer_patterns = [
        rf"(?:therefore|thus|hence)"
        rf"[^0-9+\-]*({number_pattern})",

        rf"(?:the answer is|the result is)"
        rf"[^0-9+\-]*({number_pattern})",
    ]

    for pattern in final_answer_patterns:
        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if matches:
            return matches[-1]

    # 4. Fallback: use the last numerical value.
    numbers = re.findall(number_pattern, text)

    if numbers:
        return numbers[-1]

    return None


def check_math_correctness(
    expected_output: str,
    actual_output: str,
) -> dict:
    """
    Check mathematical answers using Python Decimal.

    Prioritizes explicit final answers over intermediate
    calculations and verification values.
    """

    expected_value_text = extract_numerical_answer(
        expected_output
    )

    actual_value_text = extract_numerical_answer(
        actual_output
    )

    if expected_value_text is None or actual_value_text is None:
        return {
            "passed": False,
            "expected_value": expected_value_text,
            "actual_value": actual_value_text,
            "reason": "Could not extract numerical answers.",
        }

    try:
        expected_value = Decimal(expected_value_text)
        actual_value = Decimal(actual_value_text)

    except InvalidOperation:
        return {
            "passed": False,
            "expected_value": expected_value_text,
            "actual_value": actual_value_text,
            "reason": "Invalid numerical value.",
        }

    passed = expected_value == actual_value

    return {
        "passed": passed,
        "expected_value": str(expected_value),
        "actual_value": str(actual_value),
        "reason": (
            "Numerical answers match."
            if passed
            else "Numerical answers do not match."
        ),
    }


def get_evaluation_metrics():
    """
    Create evaluation metrics using the local Ollama judge.
    """

    judge_model = get_judge_model()

    answer_relevancy = AnswerRelevancyMetric(
        model=judge_model,
        threshold=0.7,
        include_reason=True,
        async_mode=False,
    )

    correctness = GEval(
        name="Correctness",
        evaluation_steps=[
            "Compare the actual output with the expected output.",
            "Check whether the actual output contains correct information.",
            "Penalize factual contradictions and important missing details.",
            "Accept mathematically equivalent numerical representations.",
            "Evaluate the meaning of the answer, not just its exact wording.",
        ],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        model=judge_model,
        threshold=0.7,
        async_mode=False,
        verbose_mode=False,
    )

    return [
        answer_relevancy,
        correctness,
    ]
