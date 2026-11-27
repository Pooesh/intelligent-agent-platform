
from langgraph.graph import StateGraph, START, END

from app.orchestration.state import AgentState

from app.agents.supervisor import SupervisorAgent
from app.agents.coding_agent import CodingAgent
from app.agents.math_agent import MathAgent
from app.agents.research_agent import ResearchAgent
from app.agents.general_agent import GeneralAgent


class AgentWorkflow:

    def __init__(self):

        self.supervisor = SupervisorAgent()

        self.coding_agent = CodingAgent()
        self.math_agent = MathAgent()
        self.research_agent = ResearchAgent()
        self.general_agent = GeneralAgent()

        self.workflow = self._build_workflow()

    async def supervisor_node(self, state: AgentState) -> dict:

        selected_agent = await self.supervisor.classify_query(
            state["user_query"]
        )

        print(f"Supervisor selected: {selected_agent}")

        return {
            "selected_agent": selected_agent
        }

    async def coding_node(self, state: AgentState) -> dict:

        response = await self.coding_agent.process(
            state["user_query"]
        )

        return {
            "agent_response": response
        }

    async def math_node(self, state: AgentState) -> dict:

        response = await self.math_agent.process(
            state["user_query"]
        )

        return {
            "agent_response": response
        }

    async def research_node(self, state: AgentState) -> dict:

        response = await self.research_agent.process(
            state["user_query"]
        )

        return {
            "agent_response": response
        }

    async def general_node(self, state: AgentState) -> dict:

        response = await self.general_agent.process(
            state["user_query"]
        )

        return {
            "agent_response": response
        }

    @staticmethod
    def route_to_agent(state: AgentState) -> str:

        selected_agent = state["selected_agent"]

        if selected_agent == "coding":
            return "coding"

        if selected_agent == "math":
            return "math"

        if selected_agent == "research":
            return "research"

        return "general"

    def _build_workflow(self):

        graph = StateGraph(AgentState)

        graph.add_node("supervisor", self.supervisor_node)

        graph.add_node("coding", self.coding_node)
        graph.add_node("math", self.math_node)
        graph.add_node("research", self.research_node)
        graph.add_node("general", self.general_node)

        graph.add_edge(START, "supervisor")

        graph.add_conditional_edges(
            "supervisor",
            self.route_to_agent,
            {
                "coding": "coding",
                "math": "math",
                "research": "research",
                "general": "general",
            },
        )

        graph.add_edge("coding", END)
        graph.add_edge("math", END)
        graph.add_edge("research", END)
        graph.add_edge("general", END)

        return graph.compile()

    async def run(self, user_query: str) -> AgentState:

        initial_state = {
            "user_query": user_query,
            "selected_agent": "",
            "agent_response": "",
        }

        result = await self.workflow.ainvoke(initial_state)

        return result
