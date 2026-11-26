
import pytest

from app.agents.supervisor import SupervisorAgent
from app.evaluation.metrics import check_math_correctness
from app.evaluation.code_validator import validate_java_code
from app.evaluation import evaluator


@pytest.fixture
def supervisor():
    return SupervisorAgent()


# -------------------------------
# Supervisor Routing Tests
# -------------------------------

@pytest.mark.parametrize(
    "query, expected_agent",
    [
        ("Write a Java program to reverse a string.", "coding"),
        ("Explain Java Stream API filter().", "coding"),
        ("Calculate 25 percent of 800.", "math"),
        ("What is the square root of 144?", "math"),
        ("Compare LangGraph, CrewAI and AutoGen.", "research"),
        ("Explain LangGraph architecture.", "research"),
        ("What is cloud computing?", "general"),
        (
            "What are the benefits of problem-solving skills?",
            "general",
        ),
    ],
)
@pytest.mark.asyncio
async def test_supervisor_routing(supervisor, query, expected_agent):
    result = await supervisor.classify_query(query)

    assert result == expected_agent


# -------------------------------
# Deterministic Math Tests
# -------------------------------

@pytest.mark.parametrize(
    "expected, actual",
    [
        ("200", "The answer is 200."),
        ("12", "The square root of 144 is 12."),
        ("200", "200.0"),
        ("25", "The result is 25."),
    ],
)
def test_math_correctness_passes(expected, actual):
    result = check_math_correctness(expected, actual)

    assert result["passed"] is True


@pytest.mark.parametrize(
    "expected, actual",
    [
        ("200", "The answer is 150."),
        ("12", "The square root is 15."),
        ("25", "The result is 30."),
    ],
)
def test_math_correctness_fails(expected, actual):
    result = check_math_correctness(expected, actual)

    assert result["passed"] is False


# -------------------------------
# Java Compilation Tests
# -------------------------------

def test_java_compilation_passes():

    valid_java_code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
"""

    result = validate_java_code(valid_java_code)

    assert result["passed"] is True
    assert result["stage"] == "compilation"


def test_java_compilation_fails():

    invalid_java_code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello World")
    }
}
"""

    result = validate_java_code(invalid_java_code)

    assert result["passed"] is False
    assert result["stage"] == "compilation"
    assert "error" in result["reason"].lower()


# -------------------------------
# DeepEval Timeout Handling Tests
# -------------------------------

@pytest.mark.asyncio
async def test_evaluation_handles_metric_timeout(monkeypatch):
    """
    Verify that a DeepEval timeout is recorded as ERROR
    instead of crashing the evaluation.
    """

    class FakeMetric:

        threshold = 0.7

        def measure(self, test_case):
            raise TimeoutError("Simulated DeepEval timeout")

    async def fake_agent_invoke(state):
        return {
            "user_query": state["user_query"],
            "selected_agent": "general",
            "agent_response": "Cloud computing provides computing services.",
        }

    monkeypatch.setattr(
        evaluator.agent_graph,
        "ainvoke",
        fake_agent_invoke,
    )

    monkeypatch.setattr(
        evaluator,
        "get_evaluation_metrics",
        lambda: [FakeMetric()],
    )

    case = {
        "user_query": "What is cloud computing?",
        "expected_agent": "general",
        "expected_answer": "A clear explanation of cloud computing.",
        "evaluation_type": "general",
    }

    result = await evaluator.evaluate_case(case)

    assert len(result["metrics"]) == 1

    metric_result = result["metrics"][0]

    assert metric_result["status"] == "ERROR"
    assert metric_result["passed"] is None
    assert metric_result["score"] is None
    assert "Simulated DeepEval timeout" in metric_result["reason"]
