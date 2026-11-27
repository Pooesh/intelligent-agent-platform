
from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentRequest, AgentResponse
from app.orchestration.graph import agent_graph
from app.observability.execution_tracker import ExecutionTracker
from app.observability.execution_repository import ExecutionRepository


router = APIRouter(
    prefix="/agents",
    tags=["Multi-Agent System"],
)


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):

    tracker = ExecutionTracker(request.user_query)
    repository = ExecutionRepository()

    try:

        result = await agent_graph.ainvoke({
            "user_query": request.user_query,
            "selected_agent": "",
            "agent_response": "",
        })

        execution_record = tracker.complete(
            result["selected_agent"]
        )

    except Exception as exc:

        execution_record = tracker.fail(exc)

        try:
            await repository.save_execution(execution_record)

        except Exception as db_exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Agent processing failed: {str(exc)}. "
                    f"Execution record could not be saved: {str(db_exc)}"
                ),
            ) from db_exc

        raise HTTPException(
            status_code=502,
            detail=f"Agent processing failed: {str(exc)}",
        ) from exc

    try:

        await repository.save_execution(execution_record)

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail=(
                "Agent response was generated, "
                "but execution tracking could not be saved."
            ),
        ) from exc

    return AgentResponse(
        selected_agent=result["selected_agent"],
        agent_response=result["agent_response"],
    )
