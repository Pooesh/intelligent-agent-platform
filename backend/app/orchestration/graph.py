
from langgraph.graph import StateGraph, START, END

from app.orchestration.state import AgentState

from app.agents.supervisor import SupervisorAgent
from app.agents.coding_agent import CodingAgent
from app.agents.math_agent import MathAgent
from app.agents.research_agent import ResearchAgent
from app.agents.general_agent import GeneralAgent


# Initialize all agents
supervisor_agent = SupervisorAgent()
coding_agent = CodingAgent()
math_agent = MathAgent()
research_agent = ResearchAgent()
general_agent = GeneralAgent()


# Supervisor node
async def supervisor_node(state: AgentState) -> dict:

    selected_agent = await supervisor_agent.classify_query(
        state["user_query"]
    )

    return {
        "selected_agent": selected_agent
    }


# Coding Agent node
async def coding_node(state: AgentState) -> dict:

    response = await coding_agent.process(
        state["user_query"]
    )

    return {
        "agent_response": response
    }


# Math Agent node
async def math_node(state: AgentState) -> dict:

    response = await math_agent.process(
        state["user_query"]
    )

    return {
        "agent_response": response
    }


# Research Agent node
async def research_node(state: AgentState) -> dict:

    response = await research_agent.process(
        state["user_query"]
    )

    return {
        "agent_response": response
    }


# General Agent node
async def general_node(state: AgentState) -> dict:

    response = await general_agent.process(
        state["user_query"]
    )

    return {
        "agent_response": response
    }


# Conditional routing function
def route_query(state: AgentState) -> str:

    selected_agent = state["selected_agent"]

    if selected_agent == "coding":
        return "coding"

    elif selected_agent == "math":
        return "math"

    elif selected_agent == "research":
        return "research"

    else:
        return "general"


# Create LangGraph workflow
workflow = StateGraph(AgentState)


# Register nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("coding", coding_node)
workflow.add_node("math", math_node)
workflow.add_node("research", research_node)
workflow.add_node("general", general_node)


# Connect workflow
workflow.add_edge(START, "supervisor")


# Connect Supervisor to the selected specialist
workflow.add_conditional_edges(
    "supervisor",
    route_query,
    {
        "coding": "coding",
        "math": "math",
        "research": "research",
        "general": "general",
    }
)


# Connect specialist agents to the end
workflow.add_edge("coding", END)
workflow.add_edge("math", END)
workflow.add_edge("research", END)
workflow.add_edge("general", END)


# Compile the graph
agent_graph = workflow.compile()
