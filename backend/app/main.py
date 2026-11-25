from contextlib import asynccontextmanager
from app.api.v1.endpoints.agents import router as agents_router
from fastapi import FastAPI

from app.core.config import settings

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.llm import router as llm_router

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)

from app.database.redis import (
    connect_to_redis,
    close_redis_connection,
)


# Manage application startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup: Connect to databases
    await connect_to_mongodb()
    await connect_to_redis()

    print("Application startup completed")

    try:
        yield

    finally:
        # Shutdown: Close database connections
        await close_redis_connection()
        await close_mongodb_connection()

        print("Application shutdown completed")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


# Register API routers
app.include_router(
    health_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    llm_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    agents_router,
    prefix=settings.api_v1_prefix,
)



@app.get("/")
def root():
    return {
        "message": "Welcome to AI Intelligent Platform",
        "status": "running",
    }
