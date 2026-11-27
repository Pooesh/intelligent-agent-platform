
from typing import Any

from app.database.mongodb import mongodb_database


class ExecutionRepository:

    def __init__(self):
        self.collection = mongodb_database["execution_logs"]

    async def save_execution(
        self,
        execution_record: dict[str, Any],
    ) -> None:
        """
        Save an agent execution record to MongoDB.
        """

        await self.collection.insert_one(execution_record)

    async def get_execution(
        self,
        execution_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve an execution record using its ID.
        """

        execution = await self.collection.find_one(
            {"execution_id": execution_id},
            {"_id": 0},
        )

        return execution

    async def get_recent_executions(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most recent execution records.
        """

        cursor = (
            self.collection
            .find({}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)
