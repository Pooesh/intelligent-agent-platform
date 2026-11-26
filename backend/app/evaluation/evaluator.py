
import json
import re

from pathlib import Path

from app.orchestration.graph import agent_graph
from app.evaluation.test_cases import EVALUATION_CASES
from app.evaluation.metrics import (
    get_evaluation_metrics,
    check_math_correctness,
)
from app.evaluation.code_validator import validate_java_code

from deepeval.test_case import LLMTestCase


# Save evaluation results inside the backend directory.
RESULTS_FILE = (
    Path(__file__).resolve().parents[2]
    / "evaluation_results.json"
)


def extract_java_code(response: str) -> str | None:
    """
    Extract Java source code from a Markdown Java code block.
    """

    java_blocks = re.findall(
        r"```java\s*(.*?)```",
        response,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not java_blocks:
        return None

    return java_blocks[0].strip()


def save_evaluation_results(
    results: list[dict],
    results_path: str | Path = RESULTS_FILE,
) -> None:
    """
    Save evaluation results incrementally.

    Previous results are preserved if a later case fails.
    """

    output_path = Path(results_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


async def evaluate_case(
    case: dict,
    metrics: list | None = None,
) -> dict:
    """
    Execute and evaluate one test case.

    If metrics are supplied, use those DeepEval metrics.
    Otherwise, initialize the configured evaluation metrics.
    """

    # 1. Execute the multi-agent graph.
    result = await agent_graph.ainvoke(
        {
            "user_query": case["user_query"],
            "selected_agent": "",
            "agent_response": "",
        }
    )

    selected_agent = result["selected_agent"]
    actual_output = result["agent_response"]

    # 2. Check Supervisor routing.
    routing_correct = (
        selected_agent == case["expected_agent"]
    )

    metric_results = []

    # 3. Run DeepEval only when metrics are provided.
    if metrics is None:
        metrics = get_evaluation_metrics()

    if metrics:

        test_case = LLMTestCase(
            input=case["user_query"],
            actual_output=actual_output,
            expected_output=case["expected_answer"],
        )

        for metric in metrics:

            # Math correctness uses deterministic validation.
            if (
                case["evaluation_type"] == "math"
                and metric.__class__.__name__ == "GEval"
            ):
                continue

            metric_name = metric.__class__.__name__

            try:
                metric.measure(test_case)

                score = metric.score
                threshold = metric.threshold

                metric_results.append(
                    {
                        "metric": metric_name,
                        "score": score,
                        "threshold": threshold,
                        "passed": (
                            score is not None
                            and score >= threshold
                        ),
                        "status": "COMPLETED",
                        "reason": metric.reason,
                    }
                )

            except Exception as exc:

                metric_results.append(
                    {
                        "metric": metric_name,
                        "score": None,
                        "threshold": metric.threshold,
                        "passed": None,
                        "status": "ERROR",
                        "reason": (
                            f"{type(exc).__name__}: {str(exc)}"
                        ),
                    }
                )

                print(
                    f"Warning: {metric_name} could not evaluate "
                    f"this case: {type(exc).__name__}: {exc}"
                )

    # 4. Run deterministic math correctness.
    if case["evaluation_type"] == "math":

        math_result = check_math_correctness(
            expected_output=case["expected_answer"],
            actual_output=actual_output,
        )

        metric_results.append(
            {
                "metric": "DeterministicMathCorrectness",
                "score": (
                    1.0 if math_result["passed"] else 0.0
                ),
                "threshold": 1.0,
                "passed": math_result["passed"],
                "status": "COMPLETED",
                "reason": math_result["reason"],
                "expected_value": math_result["expected_value"],
                "actual_value": math_result["actual_value"],
            }
        )

    # 5. Validate generated Java code.
    if (
        case["evaluation_type"] == "coding"
        and "java" in case["user_query"].lower()
    ):

        java_code = extract_java_code(actual_output)

        if java_code:
            code_result = validate_java_code(java_code)

        else:
            code_result = {
                "passed": False,
                "stage": "extraction",
                "reason": (
                    "No Java code block found in the agent response."
                ),
            }

        metric_results.append(
            {
                "metric": "JavaCompilation",
                "score": (
                    1.0 if code_result["passed"] else 0.0
                ),
                "threshold": 1.0,
                "passed": code_result["passed"],
                "status": "COMPLETED",
                "reason": code_result["reason"],
                "stage": code_result["stage"],
            }
        )

    # 6. Return evaluation results.
    return {
        "user_query": case["user_query"],
        "expected_agent": case["expected_agent"],
        "selected_agent": selected_agent,
        "routing_correct": routing_correct,
        "actual_output": actual_output,
        "metrics": metric_results,
        "status": "COMPLETED",
    }


async def evaluate_dataset(
    max_cases: int | None = 1,
    run_llm_judge: bool = False,
    results_path: str | Path = RESULTS_FILE,
) -> list[dict]:
    """
    Evaluate test cases sequentially with resource-conscious defaults.

    Defaults:
        max_cases=1:
            Run only one test case.

        run_llm_judge=False:
            Skip expensive LLM-as-a-Judge requests.

        results_path:
            Save results after every completed case.
    """

    if max_cases is not None and max_cases < 1:
        raise ValueError("max_cases must be at least 1 or None.")

    cases = (
        EVALUATION_CASES[:max_cases]
        if max_cases is not None
        else EVALUATION_CASES
    )

    results = []

    # Initialize DeepEval metrics only when explicitly requested.
    metrics = (
        get_evaluation_metrics()
        if run_llm_judge
        else []
    )

    print("=" * 65)
    print("RESOURCE-CONSCIOUS AGENT EVALUATION")
    print("=" * 65)

    print(f"Test cases selected: {len(cases)}")
    print(f"LLM judge enabled: {run_llm_judge}")
    print(f"Results file: {results_path}")

    # Process one case at a time.
    for index, case in enumerate(cases, start=1):

        print(
            f"\nEvaluating case {index}/{len(cases)}: "
            f"{case['evaluation_type']}"
        )

        try:
            result = await evaluate_case(
                case=case,
                metrics=metrics,
            )

        except Exception as exc:

            print(
                f"Case {index} failed: "
                f"{type(exc).__name__}: {exc}"
            )

            result = {
                "user_query": case["user_query"],
                "expected_agent": case["expected_agent"],
                "selected_agent": None,
                "routing_correct": False,
                "actual_output": "",
                "metrics": [],
                "status": "ERROR",
                "error": f"{type(exc).__name__}: {str(exc)}",
            }

        results.append(result)

        # Save immediately after every case.
        save_evaluation_results(
            results=results,
            results_path=results_path,
        )

        print(f"Selected agent: {result['selected_agent']}")
        print(f"Routing correct: {result['routing_correct']}")
        print(f"Case status: {result['status']}")

        for metric_result in result["metrics"]:
            print(
                f"{metric_result['metric']}: "
                f"{metric_result['score']} "
                f"[{metric_result['status']}]"
            )

        print("Evaluation result saved.")

    print("\nEvaluation batch completed.")

    return results
