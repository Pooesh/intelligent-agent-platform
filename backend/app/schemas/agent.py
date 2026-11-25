
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):

    user_query: str = Field(
        ...,
        min_length=1,
        description="Query submitted by the user"
    )


class AgentResponse(BaseModel):

    selected_agent: str

    agent_response: str
