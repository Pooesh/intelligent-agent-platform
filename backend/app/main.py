
import litellm
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from app.api.v1.endpoints.agents import router as agents_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.llm import router as llm_router
from app.api.v1.endpoints.observability import router as observability_router

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)

from app.database.redis import (
    connect_to_redis,
    close_redis_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("LiteLLM debug logging configured through environment")
    print("LiteLLM success callbacks:", litellm.success_callback)
    print("LiteLLM failure callbacks:", litellm.failure_callback)

    await connect_to_mongodb()
    await connect_to_redis()

    print("Application startup completed")

    try:
        yield

    finally:
        await close_redis_connection()
        await close_mongodb_connection()

        print("Application shutdown completed")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Routers
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

app.include_router(
    observability_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
def root():
    return {
        "message": "Welcome to AI Intelligent Platform",
        "status": "running",
    }
