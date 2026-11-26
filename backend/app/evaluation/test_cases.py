
from typing import TypedDict


class EvaluationCase(TypedDict):
    user_query: str
    expected_agent: str
    expected_answer: str
    evaluation_type: str


EVALUATION_CASES: list[EvaluationCase] = [

    # Coding Agent test cases
    {
        "user_query": "Write a Java program to reverse a string.",
        "expected_agent": "coding",
        "expected_answer": "A Java program that reverses a string correctly.",
        "evaluation_type": "coding",
    },
    {
        "user_query": "Explain how Java Stream API filter() works with an example.",
        "expected_agent": "coding",
        "expected_answer": "An explanation of filter() with a valid Java Stream API example.",
        "evaluation_type": "coding",
    },

    # Math Agent test cases
    {
        "user_query": "Calculate 25 percent of 800.",
        "expected_agent": "math",
        "expected_answer": "200",
        "evaluation_type": "math",
    },
    {
        "user_query": "What is the square root of 144?",
        "expected_agent": "math",
        "expected_answer": "12",
        "evaluation_type": "math",
    },

    # Research Agent test cases
    {
        "user_query": "Compare LangGraph, CrewAI and AutoGen.",
        "expected_agent": "research",
        "expected_answer": "An evidence-based comparison of LangGraph, CrewAI and AutoGen.",
        "evaluation_type": "research",
    },
    {
        "user_query": "Explain the architecture and use cases of LangGraph.",
        "expected_agent": "research",
        "expected_answer": "An explanation of LangGraph architecture and its use cases.",
        "evaluation_type": "research",
    },

    # General Agent test cases
    {
        "user_query": "What is cloud computing?",
        "expected_agent": "general",
        "expected_answer": "A clear explanation of cloud computing.",
        "evaluation_type": "general",
    },
    {
        "user_query": "What are the benefits of learning problem-solving skills?",
        "expected_agent": "general",
        "expected_answer": "An explanation of the benefits of problem-solving skills.",
        "evaluation_type": "general",
    },
]
