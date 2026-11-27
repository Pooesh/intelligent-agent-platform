
import asyncio

from app.database.mongodb import (
    connect_to_mongodb,
    mongodb_client,
)
from app.agents.supervisor import SupervisorAgent


async def main():
    try:
        await connect_to_mongodb()

        supervisor = SupervisorAgent()

        queries = [
            "Write a Java program to reverse a string",
            "Calculate 25 percent of 800",
            "Compare LangGraph and CrewAI",
            "What is cloud computing?",
            "Explain dependency injection",
        ]

        for query in queries:
            result = await supervisor.classify_query(query)

            print(f"\nQuery: {query}")
            print(f"Category: {result}")

    finally:
        await mongodb_client.close()


if __name__ == "__main__":
    asyncio.run(main())
