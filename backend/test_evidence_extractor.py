
import pytest

from app.agents.research.evidence_extractor import EvidenceExtractor


@pytest.mark.anyio
async def test_evidence_extraction(monkeypatch):

    extractor = EvidenceExtractor()

    search_results = [
        {
            "title": "LangGraph Overview",
            "url": "https://docs.langchain.com/oss/python/langgraph/overview",
            "content": (
                "LangGraph is a low-level orchestration framework "
                "for building, managing, and deploying long-running, "
                "stateful agents. "
                "It provides graph-based orchestration capabilities."
            )
        },
        {
            "title": "CrewAI Introduction",
            "url": "https://docs.crewai.com/",
            "content": (
                "CrewAI is a framework for orchestrating role-playing, "
                "autonomous AI agents. "
                "It supports agents, tasks, crews, and processes."
            )
        }
    ]

    async def mock_generate_response(*args, **kwargs):
        return '{"source_index": 0, "sentence_id": 0, "feature": "Orchestration"}'

    monkeypatch.setattr(
        extractor.llm_service,
        "generate_response",
        mock_generate_response
    )

    evidence = await extractor.extract(search_results)

    assert isinstance(evidence, list)

    for item in evidence:
        assert item["framework"] in ["LangGraph", "CrewAI"]
        assert item["feature"]
        assert item["description"]
        assert item["source_url"]
        assert item["supporting_evidence"]
        assert item["verification_status"] == "exact_match"
        assert item["verification_method"] == "deterministic"
