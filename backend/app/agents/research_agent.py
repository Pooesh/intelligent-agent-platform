
from urllib.parse import urlparse

from app.llm.llm_service import LLMService
from app.services.web_search_service import WebSearchService
from app.agents.research.evidence_extractor import EvidenceExtractor


class ResearchAgent:

    def __init__(self):
        self.llm_service = LLMService()
        self.web_search_service = WebSearchService()
        self.evidence_extractor = EvidenceExtractor()

    def _get_source_framework(self, url: str) -> str | None:
        """
        Validate official HTTPS source URLs and identify
        which framework the documentation belongs to.

        GitHub issue, pull request, discussion, and other
        non-documentation pages are rejected.
        """

        try:
            if not isinstance(url, str) or not url.strip():
                return None

            parsed_url = urlparse(url.strip())

            if parsed_url.scheme.lower() != "https":
                return None

            hostname = (parsed_url.hostname or "").lower()

            path = parsed_url.path.lower().rstrip("/")
            path = "/" + "/".join(
                part for part in path.split("/") if part
            )

            # Reject non-documentation GitHub pages.
            if hostname == "github.com":

                path_segments = [
                    segment
                    for segment in path.split("/")
                    if segment
                ]

                if len(path_segments) < 2:
                    return None

                repository_path = "/".join(path_segments[:2])

                rejected_sections = {
                    "issues",
                    "pull",
                    "pulls",
                    "discussions",
                    "actions",
                    "projects",
                    "wiki",
                    "security",
                    "commit",
                    "commits",
                    "releases",
                    "tags",
                    "branches",
                    "stargazers",
                    "forks",
                    "watchers",
                    "network",
                    "compare",
                    "blame",
                }

                if any(
                    segment in rejected_sections
                    for segment in path_segments[2:]
                ):
                    return None

                # LangGraph official GitHub repository.
                if repository_path == "langchain-ai/langgraph":
                    return "LangGraph"

                # CrewAI official GitHub repository.
                if repository_path == "crewaiinc/crewai":
                    return "CrewAI"

                # AutoGen official GitHub repository.
                if repository_path == "microsoft/autogen":
                    return "AutoGen"

                return None

            # LangGraph official Python and JavaScript documentation.
            if hostname == "docs.langchain.com":

                path_segments = [
                    segment
                    for segment in path.split("/")
                    if segment
                ]

                valid_langgraph_paths = {
                    ("oss", "python", "langgraph"),
                    ("oss", "javascript", "langgraph"),
                }

                if tuple(path_segments[:3]) in valid_langgraph_paths:
                    return "LangGraph"

            # CrewAI official documentation.
            if hostname == "docs.crewai.com":
                return "CrewAI"

            # Microsoft AutoGen official documentation.
            if (
                hostname == "microsoft.github.io"
                and path.startswith("/autogen")
            ):
                return "AutoGen"

            return None

        except (ValueError, TypeError):
            return None

    @staticmethod
    def _is_archived_autogen_source(result: dict) -> bool:
        """
        Reject archived AutoGen GitHub repository content.

        Official AutoGen documentation pages are not rejected
        by this check.
        """

        url = result.get("url", "")

        if not isinstance(url, str):
            return False

        try:
            parsed_url = urlparse(url)

            path_segments = [
                segment.lower()
                for segment in parsed_url.path.split("/")
                if segment
            ]

            if (
                (parsed_url.hostname or "").lower() != "github.com"
                or path_segments[:2] != ["microsoft", "autogen"]
            ):
                return False

        except ValueError:
            return False

        title = result.get("title", "")
        content = result.get("content", "")

        combined_text = f"{title} {content}".lower()

        archive_indicators = [
            "this repository has been archived",
            "repository is archived",
            "autogen is now archived",
            "no longer maintained by microsoft",
        ]

        return any(
            indicator in combined_text
            for indicator in archive_indicators
        )

    async def process(self, user_query: str) -> str:

        # Step 1: Retrieve web research.
        search_results = await self.web_search_service.search(
            query=user_query,
            max_results=5
        )

        if not search_results:
            return "No relevant research sources were found."

        # Step 2: Keep only approved official sources.
        official_results = []

        rejected_sources = 0

        for result in search_results:

            if not isinstance(result, dict):
                rejected_sources += 1
                continue

            framework = self._get_source_framework(
                result.get("url", "")
            )

            if not framework:
                rejected_sources += 1
                continue

            # Reject archived AutoGen GitHub repository pages.
            if (
                framework == "AutoGen"
                and self._is_archived_autogen_source(result)
            ):
                print(
                    "Rejected archived AutoGen source:",
                    result.get("url")
                )
                rejected_sources += 1
                continue

            result["framework"] = framework
            official_results.append(result)

        print(
            f"\nApproved official sources: {len(official_results)}"
        )

        print(
            f"Rejected sources: {rejected_sources}"
        )

        if not official_results:
            return (
                "I couldn't find sufficient information in the "
                "approved official documentation sources. "
                "Please try a more specific research query."
            )

        # Step 3: Extract and validate structured evidence.
        print("\nStarting structured evidence extraction...")

        validated_evidence = await self.evidence_extractor.extract(
            official_results
        )

        if not validated_evidence:
            return (
                "The official documentation sources were found, "
                "but no sufficiently verifiable evidence could be "
                "extracted. Please try a more specific research query."
            )

        print(
            f"Validated research evidence: {len(validated_evidence)}"
        )

        # Step 4: Build trusted source mapping.
        source_lookup = {
            result["url"]: result
            for result in official_results
            if isinstance(result.get("url"), str)
        }

        framework_evidence = {
            "LangGraph": [],
            "CrewAI": [],
            "AutoGen": [],
        }

        sources = []
        source_id_map = {}

        for item in validated_evidence:

            source_url = item.get("source_url")

            if not isinstance(source_url, str):
                continue

            original_source = source_lookup.get(source_url)

            if not original_source:
                continue

            # Determine framework using the official URL.
            framework = self._get_source_framework(source_url)

            if framework not in framework_evidence:
                continue

            # Assign one reference ID per unique source URL.
            if source_url not in source_id_map:

                source_id = len(sources) + 1
                source_id_map[source_url] = source_id

                sources.append({
                    "id": source_id,
                    "framework": framework,
                    "title": original_source.get(
                        "title",
                        "Untitled source"
                    ),
                    "url": source_url,
                })

            source_id = source_id_map[source_url]

            # Build evidence context.
            framework_evidence[framework].append({
                "source_id": source_id,
                "feature": item["feature"],
                "description": item["description"],
                "architecture": item.get(
                    "architecture",
                    "Not established"
                ),
                "supporting_evidence": item["supporting_evidence"],
            })

        # Step 5: Check evidence availability for each framework.
        frameworks_with_evidence = {
            framework
            for framework, items in framework_evidence.items()
            if items
        }

        missing_frameworks = [
            framework
            for framework in framework_evidence
            if framework not in frameworks_with_evidence
        ]

        print(
            "\nFrameworks with validated evidence:",
            sorted(frameworks_with_evidence)
        )

        print(
            "Frameworks without validated evidence:",
            missing_frameworks
        )

        # Step 6: Stop unsupported comparisons.
        if missing_frameworks:

            available = (
                ", ".join(sorted(frameworks_with_evidence))
                if frameworks_with_evidence
                else "None"
            )

            missing = ", ".join(missing_frameworks)

            return (
                "A complete comparison cannot be generated because "
                "validated official evidence is missing.\n\n"
                f"Frameworks with validated evidence: {available}\n"
                f"Frameworks without validated evidence: {missing}\n\n"
                "Please retrieve additional official documentation "
                "before generating a complete comparison."
            )

        # Step 7: Build framework-specific evidence context.
        grouped_context = []

        for framework, evidence_items in framework_evidence.items():

            grouped_context.append(
                f"\n### {framework} OFFICIAL EVIDENCE\n"
            )

            for item in evidence_items:

                grouped_context.append(
                    f"""
Evidence:
Feature: {item["feature"]}
Description: {item["description"]}
Architecture: {item["architecture"]}
Exact Supporting Evidence: {item["supporting_evidence"]}
Citation: [S{item["source_id"]}]
"""
                )

        context = "\n".join(grouped_context)

        # Step 8: Generate evidence-based research prompt.
        prompt = f"""
You are a research assistant. Your task is to produce an evidence-grounded
comparison of LangGraph, CrewAI, and AutoGen.

STRICT RULES:

1. Use only the validated evidence provided below.
2. Treat supporting_evidence as the source of factual information.
3. Do not treat generated descriptions or architecture fields as verified facts.
4. Do not add information from your own knowledge.
5. Do not invent features, capabilities, architecture details, or advantages.
6. If the evidence does not establish something, write:
   "Not established by retrieved official documentation."
7. Every factual claim must include its source reference ID, such as [S1].
8. Cite the reference in the same sentence as the claim.
9. Do not make an overall recommendation or rank the frameworks.
10. Do not assume that a feature available in one framework is also
    available in another.

OUTPUT FORMAT:

# Evidence-Based Framework Comparison

## 1. LangGraph

### What the retrieved evidence establishes
- List only capabilities directly supported by the evidence.
- Include source reference IDs.

### What remains unverified
- Mention important details that the available evidence does not establish.

## 2. CrewAI

### What the retrieved evidence establishes
- List only capabilities directly supported by the evidence.
- Include source reference IDs.

### What remains unverified
- Mention important details that the available evidence does not establish.

## 3. AutoGen

### What the retrieved evidence establishes
- List only capabilities directly supported by the evidence.
- Include source reference IDs.

### What remains unverified
- Mention important details that the available evidence does not establish.

## 4. Summary Table

Use exactly these three columns:

| Framework | Evidence-supported capabilities | Evidence gaps |
|---|---|---|

## 5. Conclusion

Summarize what can be concluded from the retrieved evidence.
If the evidence is insufficient to determine which framework is best,
explicitly say that a reliable overall ranking cannot be made.

VALIDATED RESEARCH EVIDENCE:

{context}

USER QUERY:

{user_query}

Remember: accuracy is more important than completeness.
Do not fill evidence gaps with assumptions.
"""

        # Step 9: Generate response.
        response = await self.llm_service.generate_response(
            message=prompt,
            provider="ollama",
        )

        # Step 10: Append references exactly once.
        references = ["## References"]

        for source in sources:
            references.append(
                f"[S{source['id']}] {source['title']}\n"
                f"{source['url']}\n"
                f"Framework: {source['framework']}"
            )

        return response.strip() + "\n\n" + "\n\n".join(references)
