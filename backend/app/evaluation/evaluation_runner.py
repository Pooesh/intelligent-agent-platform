
import asyncio
from collections import defaultdict

from app.evaluation.evaluator import evaluate_dataset


def get_agent_name(agent) -> str:
    """Return a safe display name for an agent."""

    if agent is None:
        return "UNKNOWN (routing failed)"

    return str(agent).upper()


def agent_sort_key(agent):
    """Sort agent names safely, including None values."""

    return (agent is None, str(agent).lower())


def print_metric_summary(results: list[dict]) -> None:
    """Display metric scores grouped by agent."""

    agent_metrics = defaultdict(lambda: defaultdict(list))

    for result in results:
        agent = result.get("selected_agent")

        for metric in result.get("metrics", []):
            agent_metrics[agent][metric["metric"]].append(metric)

    print("\n" + "=" * 70)
    print("METRIC SUMMARY BY AGENT")
    print("=" * 70)

    if not agent_metrics:
        print("No metric results available.")
        return

    for agent, metrics in sorted(
        agent_metrics.items(),
        key=lambda item: agent_sort_key(item[0])
    ):
        print(f"\nAgent: {get_agent_name(agent)}")

        for metric_name, metric_results in sorted(metrics.items()):

            completed = [
                item for item in metric_results
                if item.get("status") == "COMPLETED"
            ]

            scores = [
                item["score"]
                for item in completed
                if item.get("score") is not None
            ]

            average = (
                sum(scores) / len(scores)
                if scores else None
            )

            passed = sum(
                1 for item in completed
                if item.get("passed") is True
            )

            errors = sum(
                1 for item in metric_results
                if item.get("status") == "ERROR"
            )

            print(
                f"  {metric_name}: "
                f"{average:.2f}" if average is not None
                else f"  {metric_name}: N/A",
                end=""
            )

            print(
                f" average | {passed}/{len(completed)} passed"
                f" | {errors} errors"
            )


def print_failed_cases(results: list[dict]) -> None:
    """Display routing, metric, and execution errors."""

    print("\n" + "=" * 70)
    print("CASES REQUIRING REVIEW")
    print("=" * 70)

    found_issues = False

    for result in results:

        if result.get("status") == "ERROR":
            found_issues = True
            print("\nExecution error:")
            print(f"  Query: {result['user_query']}")
            print(f"  Error: {result.get('error', 'Unknown error')}")

        if not result.get("routing_correct", False):
            found_issues = True
            print("\nRouting failure:")
            print(f"  Query: {result['user_query']}")
            print(f"  Expected: {result['expected_agent']}")
            print(
                f"  Selected: "
                f"{get_agent_name(result.get('selected_agent'))}"
            )

        for metric in result.get("metrics", []):

            if metric.get("status") == "ERROR":
                found_issues = True
                print(f"\nMetric evaluation error: {metric['metric']}")
                print(f"  Query: {result['user_query']}")
                print(f"  Reason: {metric.get('reason')}")

            elif metric.get("passed") is False:
                found_issues = True
                print(f"\nMetric requiring review: {metric['metric']}")
                print(
                    f"  Agent: "
                    f"{get_agent_name(result.get('selected_agent'))}"
                )
                print(f"  Query: {result['user_query']}")
                print(f"  Score: {metric.get('score')}")
                print(f"  Reason: {metric.get('reason')}")

    if not found_issues:
        print("No failures detected.")


async def main():
    """Run a limited agent evaluation and display a report."""

    print("=" * 70)
    print("AI INTELLIGENT PLATFORM - AGENT EVALUATION")
    print("=" * 70)

    # Safe defaults: one test case, no LLM judge.
    results = await evaluate_dataset(
        max_cases=8,
        run_llm_judge=False,
    )

    total_cases = len(results)

    correct_routes = sum(
        1 for result in results
        if result.get("routing_correct") is True
    )

    routing_accuracy = (
        correct_routes / total_cases * 100
        if total_cases else 0
    )

    agent_counts = defaultdict(int)

    for result in results:
        agent_counts[result.get("selected_agent")] += 1

    print("\n" + "=" * 70)
    print("OVERALL EVALUATION SUMMARY")
    print("=" * 70)

    print(f"Total test cases: {total_cases}")
    print(f"Correct routes: {correct_routes}/{total_cases}")
    print(f"Routing accuracy: {routing_accuracy:.2f}%")

    print("\nCases by agent:")

    for agent, count in sorted(
        agent_counts.items(),
        key=lambda item: agent_sort_key(item[0])
    ):
        print(f"  {get_agent_name(agent)}: {count}")

    print_metric_summary(results)
    print_failed_cases(results)

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETED")
    print("=" * 70)

    print(
        "LLM-as-a-Judge is disabled for this run. "
        "Deterministic checks are reported separately."
    )


if __name__ == "__main__":
    asyncio.run(main())
