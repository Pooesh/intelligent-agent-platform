
import asyncio

from app.observability.execution_tracker import ExecutionTracker
from app.observability.execution_repository import ExecutionRepository
from app.database.mongodb import connect_to_mongodb, mongodb_client


async def main():

    try:
        await connect_to_mongodb()

        tracker = ExecutionTracker(
            "Calculate 25 percent of 800"
        )

        execution_record = tracker.complete("math")

        repository = ExecutionRepository()

        await repository.save_execution(execution_record)

        print("Execution saved successfully!")

        saved_execution = await repository.get_execution(
            tracker.execution_id
        )

        print("\nRetrieved execution:")
        print(saved_execution)

        recent_executions = await repository.get_recent_executions(
            limit=5
        )

        print("\nRecent executions:")
        print(recent_executions)

    finally:
        await mongodb_client.close()


if __name__ == "__main__":
    asyncio.run(main())
