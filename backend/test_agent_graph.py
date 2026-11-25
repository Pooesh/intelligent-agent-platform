
import pytest

from app.orchestration.graph import agent_graph


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query, expected_agent",
    [
        ("Calculate 25 percent of 800.", "math"),
        ("Research the latest developments in Generative AI.", "research"),
        ("What is cloud computing?", "general"),
        ("Write a Java program to reverse a string.", "coding"),
    ],
)
async def test_agent_routing(query: str, expected_agent: str):

    result = await agent_graph.ainvoke({
        "user_query": query,
        "selected_agent": "",
        "agent_response": ""
    })

    print("\n======================================")
    print("User Query:", query)
    print("Selected Agent:", result["selected_agent"])
    print("Agent Response:")
    print(result["agent_response"])
    print("======================================")

    assert result["selected_agent"] == expected_agent
    assert result["agent_response"]
