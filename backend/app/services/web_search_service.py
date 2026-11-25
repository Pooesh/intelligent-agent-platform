
import asyncio
from typing import Any

from tavily import TavilyClient

from app.core.config import settings


class WebSearchService:

    FRAMEWORKS = {
        "LangGraph": {
            "query": (
                "LangGraph official documentation "
                "StateGraph nodes edges persistence subgraphs"
            ),
            "domains": [
                "docs.langchain.com",
                "github.com/langchain-ai",
            ],
        },
        "CrewAI": {
            "query": (
                "CrewAI official documentation "
                "agents crews flows tasks memory architecture"
            ),
            "domains": [
                "docs.crewai.com",
                "github.com/crewaiinc",
            ],
        },
        "AutoGen": {
            "query": (
                "Microsoft AutoGen official documentation "
                "agents architecture messaging runtime"
            ),
            "domains": [
                "microsoft.github.io",
                "github.com/microsoft",
            ],
        },
    }

    def __init__(self):
        if not settings.tavily_api_key:
            raise ValueError("Tavily API key is not configured.")

        self.client = TavilyClient(
            api_key=settings.tavily_api_key
        )

    async def _search_one(
        self,
        query: str,
        max_results: int,
        domains: list[str] | None = None,
    ) -> list[dict[str, Any]]:

        search_arguments = {
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }

        if domains:
            search_arguments["include_domains"] = domains

        response = await asyncio.to_thread(
            self.client.search,
            **search_arguments
        )

        results = []

        for item in response.get("results", []):

            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0.0),
                "search_query": query,
                "is_official_search": bool(domains),
            })

        return results

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[dict[str, Any]]:

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        # Step 1: Search each framework independently.
        search_tasks = []

        for framework, config in self.FRAMEWORKS.items():

            print(f"Searching official documentation: {framework}")

            search_tasks.append(
                self._search_one(
                    query=config["query"],
                    max_results=3,
                    domains=config["domains"],
                )
            )

        # Step 2: Also search using the user's original query.
        search_tasks.append(
            self._search_one(
                query=query.strip(),
                max_results=max_results,
            )
        )

        # Step 3: Execute all searches concurrently.
        search_responses = await asyncio.gather(
            *search_tasks
        )

        # Step 4: Combine results and remove duplicate URLs.
        combined_results = []
        seen_urls = set()

        for search_results in search_responses:

            for result in search_results:

                url = result.get("url", "").strip()

                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)
                combined_results.append(result)

        # Step 5: Return all unique results.
        # Do not truncate the list because that could remove
        # documentation belonging to one of the frameworks.
        print(
            f"\nTotal unique search results: {len(combined_results)}"
        )

        return combined_results
