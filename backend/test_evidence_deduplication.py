
from app.agents.research.evidence_extractor import EvidenceExtractor


def test_duplicate_evidence_is_removed():

    extractor = EvidenceExtractor()

    search_results = [
        {
            "url": "https://docs.langchain.com/oss/python/langgraph/overview",
            "content": "LangGraph is a low-level orchestration framework."
        }
    ]

    evidence = [
        {
            "framework": "LangGraph",
            "feature": "Orchestration",
            "description": "LangGraph is an orchestration framework.",
            "source_title": "LangGraph Overview",
            "source_url": "https://docs.langchain.com/oss/python/langgraph/overview",
            "supporting_evidence": "LangGraph is a low-level orchestration framework."
        },
        {
            "framework": "LangGraph",
            "feature": "Orchestration",
            "description": "LangGraph is an orchestration framework.",
            "source_title": "LangGraph Overview",
            "source_url": "https://docs.langchain.com/oss/python/langgraph/overview",
            "supporting_evidence": "LangGraph is a low-level orchestration framework."
        }
    ]

    result = extractor.validate_evidence(
        evidence,
        search_results
    )

    assert len(evidence) == 2
    assert len(result) == 1
    assert result[0]["framework"] == "LangGraph"
    assert result[0]["feature"] == "Orchestration"
