
import asyncio

from app.services.web_search_service import WebSearchService


async def main():

    search_service = WebSearchService()

    query = (
        "Compare LangGraph, CrewAI, and AutoGen. "
        "Explain their architecture, features, and use cases."
    )

    print(f"\nSearching the web for: {query}\n")

    results = await search_service.search(
        query=query,
        max_results=5
    )

    print(f"\nTotal unique results: {len(results)}")

    for index, result in enumerate(results, start=1):

        print(f"\n{'=' * 70}")
        print(f"RESULT {index}")
        print(f"{'=' * 70}")

        print("Search query:", result["search_query"])
        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Score:", result["score"])
        print("Content:", result["content"][:800])


if __name__ == "__main__":
    asyncio.run(main())
