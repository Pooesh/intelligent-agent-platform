
from typing import Any

from app.database.mongodb import mongodb_database


class CostRepository:

    def __init__(self):
        self.collection = mongodb_database["llm_usage"]

    async def save_usage(
        self,
        usage_record: dict[str, Any],
    ) -> None:
        """
        Save an LLM usage record to MongoDB.
        """

        await self.collection.insert_one(usage_record)

    async def get_recent_usage(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Retrieve recent LLM usage records.
        """

        cursor = (
            self.collection
            .find({}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def get_usage_summary(self) -> dict[str, Any]:
        """
        Calculate aggregate token usage and estimated cost.
        """

        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_prompt_tokens": {
                        "$sum": "$prompt_tokens"
                    },
                    "total_completion_tokens": {
                        "$sum": "$completion_tokens"
                    },
                    "total_tokens": {
                        "$sum": "$total_tokens"
                    },
                    "total_estimated_cost": {
                        "$sum": "$estimated_cost"
                    },
                    "total_requests": {
                        "$sum": 1
                    },
                }
            }
        ]

        cursor = await self.collection.aggregate(pipeline)

        results = await cursor.to_list(length=1)

        if not results:
            return {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "total_estimated_cost": 0.0,
                "total_requests": 0,
            }

        summary = results[0]
        summary.pop("_id", None)

        summary["total_estimated_cost"] = round(
            float(summary["total_estimated_cost"]),
            8,
        )

        return summary
