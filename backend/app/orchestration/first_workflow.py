
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# 1. State definition
class BasicState(TypedDict):
    user_query: str
    response: str


# 2. First workflow node
def process_query(state: BasicState) -> dict:

    query = state["user_query"]

    response = f"Your query was received: {query}"

    return {
        "response": response
    }


# 3. Create LangGraph workflow
workflow = StateGraph(BasicState)

workflow.add_node("process_query", process_query)

workflow.add_edge(START, "process_query")
workflow.add_edge("process_query", END)


# 4. Compile workflow
workflow_app = workflow.compile()


# 5. Execute workflow only when this file runs directly
if __name__ == "__main__":

    result = workflow_app.invoke({
        "user_query": "What is LangGraph?",
        "response": ""
    })

    print("Workflow Result:")
    print(result)
