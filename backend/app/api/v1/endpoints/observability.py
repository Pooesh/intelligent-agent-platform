
from fastapi import APIRouter, HTTPException, Query

from app.observability.execution_repository import ExecutionRepository
from app.cost_tracking.cost_repository import CostRepository


router = APIRouter(
    prefix="/observability",
    tags=["Observability"],
)

execution_repository = ExecutionRepository()
cost_repository = CostRepository()


@router.get("/executions")
async def get_recent_executions(
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Retrieve recent agent execution records.
    """

    executions = await execution_repository.get_recent_executions(
        limit=limit,
    )

    return {
        "total": len(executions),
        "executions": executions,
    }


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """
    Retrieve a specific agent execution by its ID.
    """

    execution = await execution_repository.get_execution(
        execution_id=execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail=f"Execution not found: {execution_id}",
        )

    return execution


@router.get("/usage")
async def get_recent_usage(
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Retrieve recent LLM token usage records.
    """

    usage_records = await cost_repository.get_recent_usage(
        limit=limit,
    )

    return {
        "total": len(usage_records),
        "usage_records": usage_records,
    }


@router.get("/usage/summary")
async def get_usage_summary():
    """
    Retrieve aggregated LLM token usage and estimated cost.
    """

    summary = await cost_repository.get_usage_summary()

    return summary
