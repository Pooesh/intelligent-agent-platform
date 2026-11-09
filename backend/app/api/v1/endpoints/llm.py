from fastapi import APIRouter, HTTPException

from app.llm.llm_service import LLMService
from app.schemas.llm import LLMRequest, LLMResponse


router = APIRouter(tags=["LLM"])

llm_service = LLMService()


@router.post("/llm/chat", response_model=LLMResponse)
async def chat_with_llm(request: LLMRequest):

    try:
        response = await llm_service.generate_response(
            message=request.message,
            provider=request.provider,
        )

        return LLMResponse(
            provider=request.provider,
            response=response,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider request failed: {str(error)}",
        )
