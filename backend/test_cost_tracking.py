
import asyncio

from app.database.mongodb import (
    connect_to_mongodb,
    mongodb_client,
)
from app.cost_tracking.cost_repository import CostRepository


async def main():
    try:
        await connect_to_mongodb()

        repository = CostRepository()

        records = await repository.get_recent_usage(limit=10)

        print("\nRecent LLM usage records:")

        for record in records:
            print(record)

        summary = await repository.get_usage_summary()

        print("\nLLM Usage Summary:")
        print(summary)

    finally:
        await mongodb_client.close()


if __name__ == "__main__":
    asyncio.run(main())
