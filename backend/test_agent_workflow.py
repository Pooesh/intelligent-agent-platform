
import asyncio

from app.orchestration.agent_workflow import AgentWorkflow


async def main():

    workflow = AgentWorkflow()

    test_queries = [
        "Write a Java program to reverse a string",
        "Calculate 25 percent of 800",
        "Compare LangGraph and CrewAI",
        "What is cloud computing?",
    ]

    for query in test_queries:

        print("\n" + "=" * 70)
        print(f"USER QUERY: {query}")

        result = await workflow.run(query)

        print(f"SELECTED AGENT: {result['selected_agent']}")
        print("\nAGENT RESPONSE:")
        print(result["agent_response"])


if __name__ == "__main__":
    asyncio.run(main())
