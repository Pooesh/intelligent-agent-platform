
from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentRequest, AgentResponse
from app.orchestration.graph import agent_graph


router = APIRouter(
    prefix="/agents",
    tags=["Multi-Agent System"],
)


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):

    try:

        result = await agent_graph.ainvoke({
            "user_query": request.user_query,
            "selected_agent": "",
            "agent_response": "",
        })

        return AgentResponse(
            selected_agent=result["selected_agent"],
            agent_response=result["agent_response"],
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Agent processing failed: {str(exc)}",
        ) from exc
