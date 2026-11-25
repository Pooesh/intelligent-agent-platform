
from app.agents.research.evidence_extractor import EvidenceExtractor


def test_json_array_response():

    result = EvidenceExtractor._parse_json_response("[1, 2]")

    assert isinstance(result, list)
    assert result == [1, 2]


def test_json_object_response():

    result = EvidenceExtractor._parse_json_response('{"evidence": []}')

    assert isinstance(result, dict)
    assert result == {"evidence": []}


def test_json_markdown_code_block_response():

    result = EvidenceExtractor._parse_json_response(
        '```json\n{"evidence": []}\n```'
    )

    assert isinstance(result, dict)
    assert result == {"evidence": []}
