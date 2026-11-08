
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.mongodb import mongodb_client
from app.database.redis import redis_client


router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():

    # Check MongoDB
    try:
        await mongodb_client.admin.command("ping")
        mongodb_status = "healthy"
    except Exception:
        mongodb_status = "unhealthy"

    # Check Redis
    try:
        await redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"

    # Determine overall application health
    is_healthy = (
        mongodb_status == "healthy"
        and redis_status == "healthy"
    )

    response_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "application": settings.app_name,
        "version": settings.app_version,
        "components": {
            "mongodb": mongodb_status,
            "redis": redis_status,
        },
    }

    return JSONResponse(
        status_code=200 if is_healthy else 503,
        content=response_data,
    )
