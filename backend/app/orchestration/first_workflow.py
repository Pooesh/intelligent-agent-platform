# 1. Imports
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 2. State definition
class BasicState(TypedDict):
    user_query: str
    response: str


# 3. First workflow node
def process_query(state: BasicState) -> dict:

    query = state["user_query"]

    response = f"Your query was received: {query}"

    return {
        "response": response
    }


# 4. Create LangGraph workflow
workflow = StateGraph(BasicState)

workflow.add_node("process_query", process_query)

workflow.add_edge(START, "process_query")
workflow.add_edge("process_query", END)

app = workflow.compile()

# 5. Execute the workflow
result = app.invoke({
    "user_query": "What is LangGraph?",
    "response": ""
})

# Display the result
print(result)